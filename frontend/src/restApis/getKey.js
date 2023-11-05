import axios from "axios";
export const getKey = async (data) => {
  const res = axios.post("/api/getKey", data);
  return res.data;
};
