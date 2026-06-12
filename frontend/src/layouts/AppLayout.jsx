import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext.jsx";

const links = [
  { to: "/", label: "Dashboard" },
  { to: "/properties", label: "Properties" },
  { to: "/funds", label: "Funds" },
  { to: "/maintenance-requests", label: "Requests" },
  { to: "/dss-recommendations", label: "DSS" },
  { to: "/reports", label: "Reports" },
];

export default function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="min-h-screen bg-field">
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-64 border-r border-line bg-ink text-white lg:block">
        <div className="border-b border-white/10 px-5 py-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-teal-200">CDSS</p>
          <h1 className="mt-2 text-lg font-semibold">Maintenance Funds</h1>
        </div>
        <nav className="space-y-1 px-3 py-4">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === "/"}
              className={({ isActive }) =>
                [
                  "block rounded-md px-3 py-2 text-sm font-medium",
                  isActive ? "bg-white text-ink" : "text-slate-200 hover:bg-white/10",
                ].join(" ")
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="lg:pl-64">
        <header className="sticky top-0 z-10 border-b border-line bg-white">
          <div className="flex flex-col gap-3 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
            <nav className="flex gap-2 overflow-x-auto lg:hidden">
              {links.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  end={link.to === "/"}
                  className={({ isActive }) =>
                    [
                      "whitespace-nowrap rounded-md px-3 py-2 text-sm font-semibold",
                      isActive ? "bg-ink text-white" : "bg-field text-slate-700",
                    ].join(" ")
                  }
                >
                  {link.label}
                </NavLink>
              ))}
            </nav>
            <div className="flex items-center justify-between gap-3">
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-ink">
                  {user?.full_name || "Signed in"}
                </p>
                <p className="truncate text-xs text-slate-500">{user?.role || "user"}</p>
              </div>
              <button className="btn-secondary" type="button" onClick={handleLogout}>
                Logout
              </button>
            </div>
          </div>
        </header>

        <main className="mx-auto w-full max-w-7xl px-4 py-5">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
