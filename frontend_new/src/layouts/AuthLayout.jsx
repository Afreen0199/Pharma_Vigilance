import React from 'react';
import { Outlet } from 'react-router-dom';

const AuthLayout = () => {
  return (
    <div className="min-h-screen w-full bg-white dark:bg-slate-950 flex">
      <Outlet />
    </div>
  );
};

export default AuthLayout;
