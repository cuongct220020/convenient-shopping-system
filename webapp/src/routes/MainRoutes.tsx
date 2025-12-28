import MainLayout from '../layouts/MainLayout'
import Profile from '../pages/main/profile/Profile'
import LoginInformation from '../pages/main/profile/LoginInformation'
import OldPassword from '../pages/main/profile/OldPassword'
import Authentication from '../pages/main/profile/Authentication'
import NewPassword from '../pages/main/profile/NewPassword'
import PersonalProfile from '../pages/main/profile/PersonalProfile'
import HealthProfile from '../pages/main/profile/HealthProfile'
import Favorites from '../pages/main/profile/Favorites'
import { RouteObject } from 'react-router-dom'

const ProfileRoutes: RouteObject = {
  path: 'profile',
  children: [
    {
      index: true,
      element: <Profile />
    },
    {
      path: 'login-information',
      element: <LoginInformation />
    },
    {
      path: 'old-password',
      element: <OldPassword />
    },
    {
      path: 'authentication',
      element: <Authentication />
    },
    {
      path: 'new-password',
      element: <NewPassword />
    },
    {
      path: 'personal-profile',
      element: <PersonalProfile />
    },
    {
      path: 'health-profile',
      element: <HealthProfile />
    },
    {
      path: 'favorites',
      element: <Favorites />
    }
  ]
}

const NutritionRoutes: RouteObject = {
  path: 'nutrition',
  element: <div>Nutrition Screen</div>
}

const MealRoutes: RouteObject = {
  path: 'meal',
  element: <div>Meal Screen</div>
}

const DiaryRoutes: RouteObject = {
  path: 'diary',
  element: <div>Diary Screen</div>
}

const FavoriteRoutes: RouteObject = {
  path: 'nutrition',
  element: <div>Favorite Screen</div>
}

export const MainRoutes: RouteObject = {
  path: 'main',
  element: <MainLayout />,
  children: [
    {
      index: true,
      element: <Profile />
    },
    ProfileRoutes,
    NutritionRoutes,
    MealRoutes,
    DiaryRoutes,
    FavoriteRoutes
  ]
}
