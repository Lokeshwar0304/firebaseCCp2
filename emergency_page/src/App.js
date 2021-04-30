import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
} from "react-router-dom";
import Emergency from "./components/Emergency";
import Notified from "./components/Notified";

function App() {
  return (
    <Router>
      <div>
        <Switch>
          <Route exact path="/">
            <Emergency/>
          </Route>
          <Route path="/notified/:user_id/:request_id">
            <Notified />
          </Route>
        </Switch>
      </div>
    </Router>
  );
}


export default App;
