import { createBrowserRouter } from 'react-router-dom'
import MainLayout from '../layouts/MainLayout'
import Profile from '../pages/main/Profile'
import LoginInformation from '../pages/main/LoginInformation'

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
      path: "nutrition",
      element: <div>Nutrition Screen</div>,
    },
    {
      path: "meals",
      element: <div>Meals Screen</div>,
    },
    {
      path: "diary",
      element: <div>Diary Screen</div>,
    },
    {
      path: "favorites",
      element: <div>Favorites Screen</div>,
    },
  ],
}