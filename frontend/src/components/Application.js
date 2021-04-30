import React, { useContext } from "react";
import { Router } from "@reach/router";
import SignIn from "./SignIn";
import SignUp from "./SignUp";
import Emergency from './Emergency';
import Notified from './Notified';
import UserProvider from "../providers/UserProvider";
import ProfilePage from "./ProfilePage";
import { UserContext } from "../providers/UserProvider";
import PasswordReset from "./PasswordReset";
function Application() {
  const user = useContext(UserContext);
  return (
      //   user ?
      //   <ProfilePage />
      // :
        <Router>
          <SignUp path="signUp" />
          <SignIn path="/" />
          <Emergency path='/emergency'/>
          <Notified path="/notified/:user_id/:request_id"/>
          <PasswordReset path = "passwordReset" />
        </Router>

      
      
  );
}

export default Application;