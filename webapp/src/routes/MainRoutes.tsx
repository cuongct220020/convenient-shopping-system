import { createBrowserRouter } from 'react-router-dom'
import MainLayout from '../layouts/MainLayout'
import Profile from '../pages/main/profile/Profile'
import LoginInformation from '../pages/main/profile/LoginInformation'
import OldPassword from '../pages/main/profile/OldPassword'
import Authentication from '../pages/main/profile/Authentication'
import NewPassword from '../pages/main/profile/NewPassword'
import PersonalProfile from '../pages/main/profile/PersonalProfile'
import HealthProfile from '../pages/main/profile/HealthProfile'
import Favorites from '../pages/main/profile/Favorites'
import FamilyGroup from '../pages/main/family-group/FamilyGroup'
import AddGroup from '../pages/main/family-group/AddGroup'
import GroupDetail from '../pages/main/family-group/GroupDetail'
import EditGroup from '../pages/main/family-group/EditGroup'
import UserDetail from '../pages/main/family-group/UserDetail'
import AddPlan from '../pages/main/family-group/AddPlan'
import PlanDetail from '../pages/main/family-group/PlanDetail'
import ImplementPlan from '../pages/main/family-group/ImplementPlan'
import EditPlan from '../pages/main/family-group/EditPlan'

export const MainRoutes = {
  path: "/main",
  element: <MainLayout />,
  children: [
    {
      index: true,
      element: <Profile />,
    },
    {
      path: "profile",
      element: <Profile />,
    },
    {
       path: "profile/login-information",
       element: <LoginInformation />
    },
    {
       path: "profile/old-password",
       element: <OldPassword />
    },
    {
       path: "profile/authentication",
       element: <Authentication />
    },
    {
       path: "profile/new-password",
       element: <NewPassword />
    },
    {
       path: "profile/personal-profile",
       element: <PersonalProfile />
    },
    {
       path: "profile/health-profile",
       element: <HealthProfile />
    },
    {
       path: "profile/favorites",
       element: <Favorites />
    },
    {
      path: "family-group",
      element: <FamilyGroup />,
    },
    {
      path: "family-group/add",
      element: <AddGroup />,
    },
    {
      path: "family-group/:id",
      element: <GroupDetail />,
    },
    {
      path: "family-group/:id/edit",
      element: <EditGroup />,
    },
    {
      path: "family-group/:id/user/:userId",
      element: <UserDetail />
    },
    {
      path: "family-group/:id/add-plan",
      element: <AddPlan />
    },
    {
      path: "family-group/:id/plan/:planId",
      element: <PlanDetail />
    },
    {
      path: "family-group/:id/plan/:planId/edit",
      element: <EditPlan />
    },
    {
      path: "family-group/:id/plan/:planId/implement",
      element: <ImplementPlan />
    }
  ],
}
