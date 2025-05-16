import api from "../api";

export const usePromoteUser = (setUsers, setStatusMsg) => {
  return async (username) => {
    try {
      const res = await api.put(`/admin/promote/${username}`);
      setStatusMsg(res.data.msg);
      setUsers((prev) =>
        prev.map((u) =>
          u.username === username ? { ...u, role: "therapist" } : u
        )
      );
    } catch (e) {
      setStatusMsg("Failed to promote user.");
    }
  };
};