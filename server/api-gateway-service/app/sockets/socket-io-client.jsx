import React, { useState, useEffect, useRef } from "react";
import { io } from "socket.io-client";

export default function SocketIOClient() {
  const [serverUrl, setServerUrl] = useState("http://localhost:8000");
  const [socket, setSocket] = useState(null);
  const [status, setStatus] = useState("Disconnected");
  const [username, setUsername] = useState("");
  const [category, setCategory] = useState("");
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [events, setEvents] = useState([]);
  const logRef = useRef(null);

  // Scroll log to top when events change
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = 0;
    }
  }, [events]);

  const connectSocket = () => {
    if (socket) {
      socket.disconnect();
    }

    const s = io(serverUrl, {
      transports: ["websocket"], // use ws only
      reconnectionAttempts: 5,
      timeout: 5000,
      // path: "/socket.io", // uncomment if server runs custom path
    });

    s.on("connect", () => {
      setStatus("Connected");
      log("Connected with id: " + s.id);
    });

    s.on("disconnect", (reason) => {
      setStatus("Disconnected");
      log("Disconnected: " + reason);
    });

    s.on("connect_error", (err) => {
      setStatus("Connect Error");
      log("Connect error: " + err.message);
    });

    s.on("online", (users) => {
      setOnlineUsers(users);
      log("Received online users: " + JSON.stringify(users));
    });

    s.on("message received", (data) => {
      log("Message received: " + JSON.stringify(data));
    });

    s.on("message updated", (data) => {
      log("Message updated: " + JSON.stringify(data));
    });

    s.on("order notification", (order, notification) => {
      log(
        "Order notification: " + JSON.stringify({ order, notification })
      );
    });

    setSocket(s);
  };

  const disconnectSocket = () => {
    if (socket) {
      socket.disconnect();
      setSocket(null);
      setStatus("Disconnected");
    }
  };

  const log = (msg) => {
    setEvents((prev) => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev]);
  };

  // Emit actions
  const login = () => {
    if (socket && socket.connected) {
      socket.emit("loggedInUsers", username);
      log("Emitted loggedInUsers: " + username);
    }
  };

  const getLoggedIn = () => {
    if (socket && socket.connected) {
      socket.emit("getLoggedInUsers");
      log("Emitted getLoggedInUsers");
    }
  };

  const removeUser = () => {
    if (socket && socket.connected) {
      socket.emit("removeLoggedInUser", username);
      log("Emitted removeLoggedInUser: " + username);
    }
  };

  const sendCategory = () => {
    if (socket && socket.connected) {
      socket.emit("category", category, username);
      log("Emitted category: " + category + " for " + username);
    }
  };

  return (
    <div style={{ fontFamily: "system-ui", maxWidth: 800, margin: "0 auto" }}>
      <h2>Socket.IO React Client</h2>

      <div style={{ marginBottom: 10 }}>
        <strong>Status:</strong>{" "}
        <span style={{ color: status === "Connected" ? "green" : "crimson" }}>
          {status}
        </span>
      </div>

      <div style={{ marginBottom: 10 }}>
        <input
          value={serverUrl}
          onChange={(e) => setServerUrl(e.target.value)}
          style={{ width: "70%" }}
        />
        <button onClick={connectSocket} style={{ marginLeft: 5 }}>
          Connect
        </button>
        <button onClick={disconnectSocket} style={{ marginLeft: 5 }}>
          Disconnect
        </button>
      </div>

      <div style={{ marginBottom: 10 }}>
        <input
          placeholder="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <button onClick={login} style={{ marginLeft: 5 }}>
          Login
        </button>
        <button onClick={getLoggedIn} style={{ marginLeft: 5 }}>
          Get Logged In
        </button>
        <button onClick={removeUser} style={{ marginLeft: 5 }}>
          Logout
        </button>
      </div>

      <div style={{ marginBottom: 10 }}>
        <input
          placeholder="category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        />
        <button onClick={sendCategory} style={{ marginLeft: 5 }}>
          Send Category
        </button>
      </div>

      <div style={{ marginBottom: 10 }}>
        <h3>Online Users</h3>
        <ul>
          {onlineUsers.length === 0 && <li>(none)</li>}
          {onlineUsers.map((u, i) => (
            <li key={i}>{u}</li>
          ))}
        </ul>
      </div>

      <div>
        <h3>Logs / Events</h3>
        <div
          ref={logRef}
          style={{
            background: "#111",
            color: "#0f0",
            padding: 10,
            height: 200,
            overflow: "auto",
            borderRadius: 6,
            whiteSpace: "pre-wrap",
          }}
        >
          {events.map((e, i) => (
            <div key={i}>{e}</div>
          ))}
        </div>
      </div>
    </div>
  );
}
