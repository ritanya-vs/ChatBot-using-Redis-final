import React, { useState } from "react";
import Auth from "./Auth";
import Chat from "./Chat";

const App = () => {
  const [sessionToken, setSessionToken] = useState(null);

  return (
    <div>
      {sessionToken ? <Chat sessionToken={sessionToken} /> : <Auth setSessionToken={setSessionToken} />}
    </div>
  );
};

export default App;
