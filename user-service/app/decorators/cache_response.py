import json
from functools import wraps
from sanic.response import json as sanic_json
from sanic.request import Request
from app.services.redis_service import redis_service
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Cache Decorator")

def cache_response(key_pattern: str, ttl: int, **defaults):
    """
    Decorator to cache the JSON response of a view method.
    
    :param key_pattern: Redis key pattern. Supports placeholders like {page}, {id}, {user_id}.
                        Placeholders are filled from request.args (query params) or kwargs (path params).
    :param ttl: Time-to-live in seconds.
    :param defaults: Default values for placeholders if not found in request.
    """
    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            # 1. Identify Request object and View instance
            # In Sanic class-based views: args[0] is self, args[1] is request
            req = None
            for arg in args:
                if isinstance(arg, Request):
                    req = arg
                    break
            
            # Fallback for duck typing if isinstance fails due to imports or mocking
            if not req:
                for arg in args:
                    if hasattr(arg, "url") and hasattr(arg, "args") and hasattr(arg, "ctx"):
                        req = arg
                        break

            if not req:
                logger.warning("Could not find Request object in args. Skipping cache.")
                return await f(*args, **kwargs)

            # 2. Construct the Redis Key
            try:
                # Prepare data for formatting key
                # Start with defaults
                format_data = defaults.copy()
                
                # Update with path params (kwargs from wrapper)
                format_data.update(kwargs)
                
                # Update with query params
                # request.args is {key: [val1, val2]}
                if req.args:
                    for k, v in req.args.items():
                        format_data[k] = v[0] if v else ""

                key = key_pattern.format(**format_data)
            except KeyError as e:
                # This happens if key_pattern expects a param that is missing (e.g. {id} but not in kwargs)
                logger.debug(f"Missing parameter for cache key generation: {e}. Skipping cache.")
                return await f(*args, **kwargs)
            except Exception as e:
                 logger.error(f"Error generating cache key: {e}. Skipping cache.")
                 return await f(*args, **kwargs)

            # 3. Try to get from Cache
            cached_data = await redis_service.get_cache(key)
            if cached_data:
                # logger.debug(f"Cache HIT: {key}")
                # We assume the cached data is the dict that goes into json response
                return sanic_json(cached_data)

            # 4. Execute View
            response = await f(*args, **kwargs)

            # 5. Cache the Response
            # Only cache 200 OK responses
            if response.status == 200:
                try:
                    # response.body is bytes. Parse it to ensure it's valid JSON before caching
                    if response.body:
                        body_dict = json.loads(response.body)
                        await redis_service.set_cache(key, body_dict, ttl)
                        # logger.debug(f"Cache SET: {key}")
                except Exception as e:
                    logger.error(f"Failed to cache response for {key}: {e}")

            return response
        
        return decorated_function
    return decorator
