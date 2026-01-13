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
import Notification from '../pages/main/notification/Notification'
import { Storage } from '../pages/main/food-storage/Storage'
import { AddStorage } from '../pages/main/food-storage/AddStorage'
import { StorageDetails } from '../pages/main/food-storage/StorageDetails'
import { StorageItemDetail } from '../pages/main/food-storage/StorageItemDetail'
import { AddStorageItem } from '../pages/main/food-storage/AddStorageItem'
import { Meal } from '../pages/main/meal/Meal'
import { AddMeal } from '../pages/main/meal/AddMeal'
import { MealDetail } from '../pages/main/meal/MealDetail'
import FamilyGroup from '../pages/main/family-group/FamilyGroup'
import AddGroup from '../pages/main/family-group/AddGroup'
import GroupDetail from '../pages/main/family-group/GroupDetail'
import EditGroup from '../pages/main/family-group/EditGroup'
import UserDetail from '../pages/main/family-group/UserDetail'
import AddPlan from '../pages/main/family-group/AddPlan'
import PlanDetail from '../pages/main/family-group/PlanDetail'
import ImplementPlan from '../pages/main/family-group/ImplementPlan'
import EditPlan from '../pages/main/family-group/EditPlan'

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

const FoodRoutes: RouteObject = {
  path: 'food',
  children: [
    {
      index: true,
      element: <Storage />
    },
    {
      path: 'storage/add',
      element: <AddStorage />
    },
    {
      path: 'storage/items',
      element: <StorageDetails />
    },
    {
      path: 'storage/items/detail',
      element: <StorageItemDetail />
    },
    { path: 'storage/items/add', element: <AddStorageItem /> }
  ]
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
      path: 'notification',
      element: <Notification />
    },
    {
      index: true,
      element: <Profile />
    },
    ProfileRoutes,
    NutritionRoutes,
    FoodRoutes,
    FavoriteRoutes,
    {
      path: 'family-group',
      element: <FamilyGroup />
    },
    {
      path: 'family-group/add',
      element: <AddGroup />
    },
    {
      path: 'family-group/:id',
      element: <GroupDetail />
    },
    {
      path: 'family-group/:id/edit',
      element: <EditGroup />
    },
    {
      path: 'family-group/:id/user/:userId',
      element: <UserDetail />
    },
    {
      path: 'family-group/:id/meal',
      element: <Meal />
    },
    {
      path: 'family-group/:id/meal/add',
      element: <AddMeal />
    },
    {
      path: 'family-group/:id/meal/detail',
      element: <MealDetail />
    },
    {
      path: 'family-group/:id/add-plan',
      element: <AddPlan />
    },
    {
      path: 'family-group/:id/plan/:planId',
      element: <PlanDetail />
    },
    {
      path: 'family-group/:id/plan/:planId/edit',
      element: <EditPlan />
    },
    {
      path: 'family-group/:id/plan/:planId/implement',
      element: <ImplementPlan />
    }
  ]
}
