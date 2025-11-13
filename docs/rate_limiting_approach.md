# Rate Limiting Approach

## Overview

This document describes the layered rate limiting approach implemented in the Convenient Shopping System. The approach combines infrastructure-level rate limiting (Kong API Gateway) with service-level rate limiting (application decorators) to provide comprehensive protection against various types of abuse and attacks.

## Architecture

### Layer 1: Kong API Gateway (Infrastructure-Level)

Kong provides the first line of defense with basic rate limiting configured at the API gateway level. This protects against:

- General API abuse
- Simple DoS attacks
- Excessive requests from single IP addresses

Configuration is defined in `api-gateway/kong.yml` with rate limits based on IP addresses.

### Layer 2: Service-Level Decorators (Business-Level)

The user service implements additional rate limiting with business-specific logic:

- **Email-based rate limiting**: Prevents OTP spam per email address
- **Login failure rate limiting**: Tracks failed login attempts per username/IP combination
- **Business-specific logic**: Handles complex scenarios that require service-level context

## Rate Limiting Configuration

### Kong API Gateway

| Endpoint | Rate Limit | Purpose |
|----------|------------|---------|
| All auth endpoints | 100 requests/hour/IP | General protection |
| Registration | 5 requests/15 minutes/IP | Prevent registration spam |
| OTP Request | 3 requests/5 minutes/IP | Prevent OTP spam |
| Login | 10 requests/15 minutes/IP | Prevent brute force attempts |
| Other endpoints | 1000 requests/hour/IP | General usage protection |

### Service-Level Decorators

#### `rate_limit_by_email`
- **Endpoint**: `/api/v1/auth/otp/request`
- **Limit**: 3 requests per 5 minutes per email
- **Purpose**: Prevents OTP spam per email address (beyond Kong's IP-level protection)

#### `rate_limit_per_user` 
- **Endpoint**: `/api/v1/auth/login`
- **Limit**: Business logic to increment on failed attempts, reset on success
- **Purpose**: Brute force protection with intelligent counting

#### `rate_limit_by_ip`
- **Endpoints**: Public endpoints that need additional protection
- **Limit**: Configurable per endpoint
- **Purpose**: Additional protection beyond Kong's configuration

## Benefits of Layered Approach

1. **Defense in Depth**: Multiple layers of protection increase security
2. **Infrastructure Protection**: Kong prevents most abuse from reaching services
3. **Business Logic Handling**: Service-level decorators handle complex scenarios
4. **Flexibility**: Different rate limits for different types of attacks
5. **Scalability**: Basic rate limiting at the edge reduces load on services

## Implementation Notes

- Kong configuration handles basic IP-based rate limiting
- Service decorators implement business-specific logic that Kong cannot handle
- Both layers complement each other rather than duplicate functionality
- The decorators remain necessary for scenarios requiring access to request payload data or business context