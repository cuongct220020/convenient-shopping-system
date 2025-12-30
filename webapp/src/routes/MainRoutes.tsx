import MainLayout from '../layouts/MainLayout'
import Profile from '../pages/main/profile/Profile'
import LoginInformation from '../pages/main/profile/LoginInformation'
import OldPassword from '../pages/main/profile/OldPassword'
import Authentication from '../pages/main/profile/Authentication'
import NewPassword from '../pages/main/profile/NewPassword'
import PersonalProfile from '../pages/main/profile/PersonalProfile'
import HealthProfile from '../pages/main/profile/HealthProfile'
import Favorites from '../pages/main/profile/Favorites'

export const MainRoutes = {
  path: '/main',
  element: <MainLayout />,
  children: [
    {
      index: true,
      element: <Profile />
    },
    {
      path: 'profile',
      element: <Profile />
    },
    {
      path: 'profile/login-information',
      element: <LoginInformation />
    },
    {
      path: 'profile/old-password',
      element: <OldPassword />
    },
    {
      path: 'profile/authentication',
      element: <Authentication />
    },
    {
      path: 'profile/new-password',
      element: <NewPassword />
    },
    {
      path: 'profile/personal-profile',
      element: <PersonalProfile />
    },
    {
      path: 'profile/health-profile',
      element: <HealthProfile />
    },
    {
      path: 'profile/favorites',
      element: <Favorites />
    },
    {
      path: 'nutrition',
      element: <div>Nutrition Screen</div>
    },
    {
      path: 'meals',
      element: <div>Meals Screen</div>
    },
    {
      path: 'diary',
      element: <div>Diary Screen</div>
    },
    {
      path: 'favorites',
      element: <div>Favorites Screen</div>
    }
  ]
}
