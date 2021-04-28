import React, {useState} from "react";
//import { Router, Link, Redirect } from "@reach/router";
import { signInWithGoogle, get_user_by_request } from "../firebase";
import { auth } from "../firebase";
import ProfilePage from "./ProfilePage";
import Avatar from '@material-ui/core/Avatar';
import Button from '@material-ui/core/Button';
import CssBaseline from '@material-ui/core/CssBaseline';
import TextField from '@material-ui/core/TextField';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Checkbox from '@material-ui/core/Checkbox';
import Link from '@material-ui/core/Link';
import Grid from '@material-ui/core/Grid';
import Box from '@material-ui/core/Box';
import LockOutlinedIcon from '@material-ui/icons/LockOutlined';
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';
import Container from '@material-ui/core/Container';
import Geolocation from 'react-native-geolocation-service';

const SignIn = () => {

  const classes = makeStyles((theme) => ({
    paper: {
      marginTop: theme.spacing(8),
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
    },
    avatar: {
      margin: theme.spacing(1),
      backgroundColor: theme.palette.secondary.main,
    },
    form: {
      width: '100%', // Fix IE 11 issue.
      marginTop: theme.spacing(1),
    },
    submit: {
      margin: theme.spacing(3, 0, 2),
    },
  }));

    const [isSignedIn,setSignedIn] = useState(false);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);

    const putBloodRequest = (event)=>{

      Geolocation.getCurrentPosition(
        (position) => {

          const body = {
            anonymous: true,
            face_signature: null,
            victim_id: null,
            timestamp: new Date().getTime(),
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          }

          fetch('https://us-central1-bloodbankasaservice.cloudfunctions.net/get_user_by_request',{
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(body)
          }).then(response =>{
            return response.text();
          }).then(data =>{
            console.log(data)
          }).catch(error => {
            console.log(error)
          });

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
    }

    const signInWithEmailAndPasswordHandler = (event,email, password) => {
        
        event.preventDefault();
        
        auth.signInWithEmailAndPassword(email, password).then(() => {

          setSignedIn(true);
          
          
          }).catch(error => {
        setError("Error signing in with password and email!");
          console.error("Error signing in with password and email", error);
        });
      };
      
      
      const onChangeHandler = (event) => {
          const {name, value} = event.currentTarget;
        
          if(name === 'userEmail') {
              setEmail(value);
          }
          else if(name === 'userPassword'){
            setPassword(value);
          }
      };
   

  return (
    isSignedIn? 
    <ProfilePage></ProfilePage>:
    <Container component="main" maxWidth="xs">
      <CssBaseline />
      <div className={classes.paper}>
        <Typography component="h1" variant="h5">
          Sign in
        </Typography>
        <form className={classes.form} noValidate>
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            id="email"
            label="Email Address"
            name="userEmail"
            value = {email}
            autoFocus
            onChange = {(event) => onChangeHandler(event)}
          />
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            label="Password"
            type="password"
            id="password"
            autoComplete="current-password"
            name="userPassword"
            value = {password}
            onChange = {(event) => onChangeHandler(event)}
          />
          <FormControlLabel
            control={<Checkbox value="remember" color="primary" />}
            label="Remember me"
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            className={classes.submit}
            onClick = {(event) => {signInWithEmailAndPasswordHandler(event, email, password)}}
          >
            Sign In
          </Button>

          <Button
            fullWidth
            variant="contained"
            // style={{color : 'red'}}
            className={classes.submit}
            onClick = {(event) => {putBloodRequest(event)}}
          >
            Urgent Blood Request
          </Button>

          <Grid container>
            <Grid item xs>
              <Link href="passwordReset" variant="body2">
                Forgot password?
              </Link>
            </Grid>
            <Grid item>
              <Link href="signUp" variant="body2">
                {"Don't have an account? Sign Up"}
              </Link>
            </Grid>
          </Grid>
        </form>
      </div>
    </Container>
  );
};

export default SignIn;