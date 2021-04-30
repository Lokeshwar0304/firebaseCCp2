import React, { useContext } from "react";
import { UserContext } from "../providers/UserProvider";
import { navigate } from "@reach/router";
import {auth} from "../firebase";
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';
import Button from '@material-ui/core/Button';
import { makeStyles } from '@material-ui/core/styles';
import Icon from '@material-ui/core/Icon';
import Geolocation from 'react-native-geolocation-service';
import { generateUserRequest,getUserRequestLocationData } from "../firebase";
import MapContainer from "./MapContainer";

const ProfilePage = () => {

  function processRequest(currentRequest)
  {
<<<<<<< HEAD
      // generateUserRequest(currentRequest);
     requests.add(currentRequest)
    .then( function(docRef) {
        getUserRequestLocationData(docId, callback2);
       }
       generateUserRequest(currentRequest, callback1);  
>>>>>>> d6c5bf81a11b0668b9790aa36758998dc7f45b00
  }

  const gridStyles =  {paper: {padding: 10, marginTop: 20, marginBottom:20, height:'350%' }}
  const requestBlood = () => {
    var currentRequest={}
    Geolocation.getCurrentPosition(
      (position) => {
        currentRequest={"latitude":position.coords.latitude, "longitude":position.coords.longitude,"timestamp":position.timestamp}
        currentRequest['email']=email
        processRequest(currentRequest)
      },  
      (error) => {
        console.log(error.code, error.message);
      },
      {
         enableHighAccuracy: true,
         timeout: 10000,
          maximumAge: 100000
       }
    );
  };
  const user = useContext(UserContext);
  const { displayName, email,bloodGroup} = user;
  console.log(user)
  return (
        <Grid container>
              <Grid item sm={4}>
                <Paper style={gridStyles.paper}>
                <div className = "mx-auto w-11/12 md:w-2/4 py-8 px-4 md:px-8">
                    <div className="flex border flex-col items-center md:flex-row md:items-start border-blue-400 px-3 py-4">
                      {/* <div
                        style={{
                          background: `url(${photoURL || 'https://res.cloudinary.com/dqcsk8rsc/image/upload/v1577268053/avatar-1-bitmoji_upgwhc.png'})  no-repeat center center`,
                          backgroundSize: "cover",
                          height: "200px",
                          width: "200px"
                        }}
                        className="border border-blue-300"
                      ></div> */}
                      <div className = "md:pl-4">
                      <h2 className = "text-2xl font-semibold">{displayName}</h2>
                      <h3 className = "italic">{email}</h3>
                      <h3 className ="italic">{bloodGroup}</h3>
                      </div>
                    </div>
                    <div>
                      <Button variant="contained"color="secondary" style={{margin:10}} onClick={requestBlood} >
                        Request Blood
                      </Button>
                      <Button variant="contained" color="primary" onClick = {() => {auth.signOut()}}>
                        Sign Out
                      </Button>
                    </div>
                    
                  </div>
                </Paper>
              </Grid>
              <Grid item sm >
                <Paper style={gridStyles.paper}>
                        <MapContainer>

                        </MapContainer>
                </Paper>
              </Grid>
        </Grid>
   
  ) 
};

export default ProfilePage;