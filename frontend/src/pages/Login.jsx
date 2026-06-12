import { useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";

import ErrorBanner from "../components/ErrorBanner.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { getApiError } from "../api/client.js";

export default function Login() {
  const { isAuthenticated, login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      await login(email, password);
      navigate(location.state?.from?.pathname || "/", { replace: true });
    } catch (err) {
      setError(getApiError(err, "Invalid credentials"));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="grid min-h-screen bg-field lg:grid-cols-[1.05fr_0.95fr]">
      <section className="flex items-center justify-center px-5 py-10">
        <div className="w-full max-w-md">
          <div className="mb-8">
            <p className="label">Maintenance CDSS</p>
            <h1 className="mt-2 text-3xl font-semibold text-ink">Sign in</h1>
          </div>

          <form className="panel p-5" onSubmit={handleSubmit}>
            <ErrorBanner message={error} />
            <div className="mt-4 space-y-4">
              <div>
                <label className="label" htmlFor="email">
                  Email
                </label>
                <input
                  className="field mt-1"
                  id="email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  required
                />
              </div>
              <div>
                <label className="label" htmlFor="password">
                  Password
                </label>
                <input
                  className="field mt-1"
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  required
                />
              </div>
              <button className="btn-primary w-full" disabled={submitting} type="submit">
                {submitting ? "Signing in" : "Sign in"}
              </button>
            </div>
          </form>
        </div>
      </section>
      <section className="hidden min-h-screen bg-ink px-10 py-12 text-white lg:flex lg:flex-col lg:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-teal-200">
            Property Management
          </p>
          <h2 className="mt-4 max-w-xl text-4xl font-semibold leading-tight">
            Maintenance fund allocation workspace
          </h2>
        </div>
        <div className="grid grid-cols-3 gap-3">
          {["Priority", "Funding", "Requests"].map((label) => (
            <div key={label} className="rounded-lg border border-white/15 bg-white/5 p-4">
              <p className="text-sm font-semibold">{label}</p>
              <div className="mt-8 h-2 rounded-full bg-teal-300" />
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
