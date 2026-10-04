// ruleid: hullproof-token-in-browser-storage, hullproof-token-value-in-browser-storage
localStorage.setItem("access_token", data.access_token);

// ruleid: hullproof-token-in-browser-storage
await AsyncStorage.setItem("session", JSON.stringify(s));

// ruleid: hullproof-token-value-in-browser-storage
localStorage.setItem("k1", refreshToken);

// ok: hullproof-token-in-browser-storage
localStorage.setItem("theme", "dark");

// ok: hullproof-token-value-in-browser-storage
localStorage.setItem("sidebar", "open");
