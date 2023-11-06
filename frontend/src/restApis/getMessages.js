
import axios from "axios";

export const getMessages = async () => {
    const res = await axios.get("http://localhost:8000/db/messages");
    return res.data;
}