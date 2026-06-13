import { api } from "./client.js";

export const propertiesApi = {
  list: () => api.get("/properties/"),
  create: (payload) => api.post("/properties/", payload),
  detail: (id) => api.get(`/properties/${id}`),
  update: (id, payload) => api.patch(`/properties/${id}`, payload),
  remove: (id) => api.delete(`/properties/${id}`),
};

export const fundsApi = {
  list: () => api.get("/funds/"),
  create: (payload) => api.post("/funds/", payload),
  update: (id, payload) => api.patch(`/funds/${id}`, payload),
  remove: (id) => api.delete(`/funds/${id}`),
};

export const maintenanceApi = {
  list: (params = {}) => api.get("/maintenance-requests/", { params }),
  create: (payload) => api.post("/maintenance-requests/", payload),
  update: (id, payload) => api.patch(`/maintenance-requests/${id}`, payload),
  remove: (id) => api.delete(`/maintenance-requests/${id}`),
};

export const dssApi = {
  rank: (payload) => api.post("/maintenance-allocations/dss/rank", payload),
  autoAllocate: (payload) => api.post("/maintenance-allocations/auto-allocate", payload),
};

export const reportsApi = {
  propertySummary: (format = "pdf") =>
    api.get("/reports/property-summary", {
      params: { format },
      responseType: "blob",
    }),
  fundAllocation: (format = "pdf") =>
    api.get("/reports/fund-allocation", {
      params: { format },
      responseType: "blob",
    }),
  maintenanceHistory: (format = "pdf") =>
    api.get("/reports/maintenance-history", {
      params: { format },
      responseType: "blob",
    }),
  monthlyFinancial: (format = "pdf") =>
    api.get("/reports/monthly-financial", {
      params: { format },
      responseType: "blob",
    }),
};
