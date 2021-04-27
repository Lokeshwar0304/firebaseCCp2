import React, { useContext, useState } from "react";
//import { Link } from "@reach/router";
import { auth, signInWithGoogle, generateUserDocument,storage } from "../firebase";
//import Select from 'react-select';
import PlacesAutocomplete, {
  geocodeByAddress,
  geocodeByPlaceId,
  getLatLng,
} from 'react-places-autocomplete';
//https://www.digitalocean.com/community/tutorials/how-to-integrate-the-google-maps-api-into-react-applications
//https://towardsdatascience.com/facial-recognition-login-system-using-deep-learning-reactjs-61bff981eb74
//https://www.youtube.com/watch?v=HjToX1WWE3w - grid layout
import Avatar from '@material-ui/core/Avatar';
import Button from '@material-ui/core/Button';
import CssBaseline from '@material-ui/core/CssBaseline';
import TextField from '@material-ui/core/TextField';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Checkbox from '@material-ui/core/Checkbox';
import Grid from '@material-ui/core/Grid';
import Box from '@material-ui/core/Box';
import LockOutlinedIcon from '@material-ui/icons/LockOutlined';
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';
import Container from '@material-ui/core/Container';
import FormGroup from '@material-ui/core/FormGroup';
import { green } from '@material-ui/core/colors';
import { withStyles } from '@material-ui/core/styles';
import Link from '@material-ui/core/Link'
import MuiPhoneNumber from "material-ui-phone-number";
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import NativeSelect from '@material-ui/core/NativeSelect';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from "@material-ui/core/MenuItem";

const SignUp = () => {

  

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
      marginTop: theme.spacing(3),
    },
    submit: {
      margin: theme.spacing(3, 0, 2),
    },
  }));

  const GreenCheckbox = withStyles({
    root: {
      color: green[400],
      '&$checked': {
        color: green[600],
      },
    },
    checked: {},
  })((props) => <Checkbox color="default" {...props} />);


  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [error, setError] = useState(null);
  const [contact, setContact]=useState("");
  const [address, setAddress]=useState("");
  const [bloodGroup, setBloodGroup]=useState("");
  const [coordinates, setCoordinates] = useState({
    lat: null,
    lng: null
  });
  const [isUser,setUserChecked] = useState(true);
  const [isHospital,setHospitalChecked] = useState(false);
  const [isBloodBank,setBloodBankChecked] = useState(false);
  const [image, setImage] = useState(null);
  const [url, setUrl] = useState("");
  const [progress, setProgress] = useState(0);


  const [bloodGroupQuan, setbloodGroupQuan] = useState([
    { itemName: 'A+', quantity: 0 },
    { itemName: 'A-', quantity: 0 },
    { itemName: 'B+', quantity: 0 },
    { itemName: 'B-', quantity: 0 },
    { itemName: 'O+', quantity: 0 },
    { itemName: 'O-', quantity: 0 },
    { itemName: 'AB+', quantity: 0 },
    { itemName: 'AB-', quantity: 0 }
  ]);
  




  const createUserWithEmailAndPasswordHandler = async (event, email, password) => {
    event.preventDefault();
    try{
      const {user} = await auth.createUserWithEmailAndPassword(email, password);
      var userType = isUser?"USER":isBloodBank?"BLOOD BANK":"HOSPITAL"
      if(isUser)
      {
        //console.log(firstName,lastName, displayName, contact,address,coordinates,bloodGroup,userType)
        generateUserDocument(user, {firstName,lastName, displayName, contact,address,coordinates,bloodGroup,userType });
      }else if(isBloodBank){
        generateUserDocument(user, {displayName, contact,address,coordinates,bloodGroupQuan,userType });
      }else{
        generateUserDocument(user, {displayName, contact,address,coordinates,bloodGroupQuan,userType });
      }
    }
    catch(error){
      setError('Error Signing up with email and password');
    }
      
    setEmail("");
    setPassword("");
    setDisplayName("");
    setContact("");
    setAddress("");
    setBloodGroup("");
    setCoordinates({lat: null,lng: null});
  };

 
  // const handleQuantityIncrease = (index) => {
  //   const newItems = [...bloodGroupQuan];
  
  //   bloodGroupQuan[index].quantity++;
  
  //   setbloodGroupQuan(newItems);
  // };

  // const handleQuantityDecrease = (index) => {
  //   const newItems = [...bloodGroupQuan];
  //   bloodGroupQuan[index].quantity--
  //   setbloodGroupQuan(newItems);
  // };

  const imageHandleChange = e => {
    if (e.target.files[0]) {
      setImage(e.target.files[0]);
    }
  };

  const imageHandleUpload = () => {
    const uploadTask = storage.ref(`images/${image.name}`).put(image);
    uploadTask.on(
      "state_changed",
      snapshot => {
        const progress = Math.round(
          (snapshot.bytesTransferred / snapshot.totalBytes) * 100
        );
        setProgress(progress);
      },
      error => {
        console.log(error);
      },
      () => {
        storage
          .ref("images")
          .child(image.name)
          .getDownloadURL()
          .then(url => {
            setUrl(url);
          });
      }
    );
  };

  const bloodGroupHandleChange = (event) => {
    setBloodGroup(event.target.value);
  };

  const handleQuantityInput = (index,event) => {
      const newItems = [...bloodGroupQuan];
      bloodGroupQuan[index].quantity= event.currentTarget.value;
      setbloodGroupQuan(newItems);
  };

  const onChangeHandler = event => {
    const { name, value } = event.currentTarget;
    if (name === "userEmail") {
      setEmail(value);
    } else if (name === "userPassword") {
      setPassword(value);
    } else if (name === "displayName") {
      setDisplayName(value);
    }else if (name === "userContact") {
      setContact(value);
    }else if(name ==="isUser"){
      setUserChecked(!isUser)
      setHospitalChecked(false)
      setBloodBankChecked(false)
    }else if(name ==="isHospital"){
      setHospitalChecked(!isHospital)
      setBloodBankChecked(false)
      setUserChecked(false)
    }else if(name ==="isBloodBank"){
      setBloodBankChecked(!isBloodBank)
      setHospitalChecked(false)
      setUserChecked(false)
    }else if(name ==="firstName"){
      setFirstName(value)
    }else if(name === "lastName"){
      setLastName(value)
    }
    
  };

  const handleSelect = async value => {
    const results = await geocodeByAddress(value);
    const latLng = await getLatLng(results[0]);
    setAddress(value);
    setCoordinates(latLng);
 
  };

  // const handleChange = bloodGroup => {
  //   setBloodGroup(bloodGroup);
 
  // };

  return (
        <Container component="main" maxWidth="xs">
        <CssBaseline />
        <div className={classes.paper}>
          <Typography component="h1" variant="h5" >
            Sign up
          </Typography>
          <form className={classes.form} noValidate>

            <Grid container spacing={3} >
              
                          {/* checkboxes */}
            
            <FormGroup row style={{ paddingLeft: 60 }}>
            <FormControlLabel
              control={<Checkbox checked={isBloodBank} onChange={event => onChangeHandler(event)}  name="isBloodBank" />}
              label="Blood Bank"
            />
            <FormControlLabel
              control={ <Checkbox checked={isHospital} onChange={event => onChangeHandler(event)}  name="isHospital" color="primary"/>}
              label="Hospital"
            />
            <FormControlLabel
              control={<GreenCheckbox checked={isUser} onChange={event => onChangeHandler(event)}  name="isUser" />}
              label="User"
            />
            </FormGroup>
            
            
          {/* checkboxes */}
              { isUser && (
              <Grid container spacing={3} >
              <Grid item xs={12} sm={6}>
                <TextField
                  autoComplete="fname"
                  name="firstName"
                  variant="outlined"
                  required
                  fullWidth
                  id="firstName"
                  label="First Name"
                  autoFocus
                  value={firstName}
                  onChange={event => onChangeHandler(event)}
                />
              </Grid>
              <Grid item xs={12} sm={6} >
                <TextField
                  variant="outlined"
                  required
                  fullWidth
                  id="lastName"
                  label="Last Name"
                  name="lastName"
                  autoComplete="lname"
                  value={lastName}
                  onChange={event => onChangeHandler(event)}
                />
              </Grid> </Grid>)}

              {(isBloodBank|| isHospital||isUser) && (
              <Grid item xs={12}>
              <TextField
              fullWidth
              required
              id="outlined-required"
              label="Name"
              variant="outlined"
              name="displayName"
              value={displayName}
              onChange={event => onChangeHandler(event)}
              />
              </Grid> )}
              <Grid item xs={12}>
                <TextField
                  variant="outlined"
                  required
                  fullWidth
                  id="email"
                  label="Email Address"
                  name="userEmail"
                  autoComplete="email"
                  value={email}
                  onChange={event => onChangeHandler(event)}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  variant="outlined"
                  required
                  fullWidth
                  name="userPassword"
                  label="Password"
                  type="password"
                  id="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={event => onChangeHandler(event)}
                />
              </Grid>
              <Grid item xs={12}>
              <MuiPhoneNumber variant="outlined" fullWidth required label="Contact Number" defaultCountry={'us'} value={contact} name="userContact" onChange={setContact}/>
              </Grid>
              
              { isUser && (
              <Grid item xs={12}>
                <FormControl variant="outlined" required fullWidth>
                <InputLabel>Blood Group</InputLabel>
                <Select
                  name="userBloodGroup"
                  value={bloodGroup}
                  onChange={bloodGroupHandleChange}
                  label="Blood Group"
                >
                  <MenuItem value="">
                    <em>None</em>
                  </MenuItem>
                  <MenuItem value={'A+'}>A+</MenuItem>
                  <MenuItem value={'A-'}>A-</MenuItem>
                  <MenuItem value={'B+'}>B+</MenuItem>
                  <MenuItem value={'B-'}>B-</MenuItem>
                  <MenuItem value={'O+'}>O+</MenuItem>
                  <MenuItem value={'O-'}>O-</MenuItem>
                  <MenuItem value={'AB+'}>AB+</MenuItem>
                  <MenuItem value={'AB-'}>AB-</MenuItem>
                </Select>
              </FormControl>
              {/* <FormControl variant="outlined" required fullWidth>
              <InputLabel >Blood Group</InputLabel>
              <Select id="userBloodGroup" value={bloodGroup}  onChange={event => onChangeHandler(event)} name="userBloodGroup">
                  {bloodGroupOptions.map(item => (
                  <option
                      key={item.value}
                      value={item.value}>
                      {item.label}
                    </option>
                  ))}
                </Select>
              </FormControl> */}
              </Grid>)}

          <Grid item xs={12}>
            <PlacesAutocomplete
          value={address}
          onChange={setAddress}
          onSelect={handleSelect}>

          {({ getInputProps, suggestions, getSuggestionItemProps, loading }) => (
                    <div>
                      <TextField variant="outlined" required fullWidth label="Type address"  {...getInputProps({ })} />
                      {/* <input {...getInputProps({ placeholder: "Type address" })} /> */}

                      <div>
                        {loading ? <div>...loading</div> : null}

                        {suggestions.map(suggestion => {
                          const style = {
                            backgroundColor: suggestion.active ? "#41b6e6" : "#fff"
                          };

                          return (
                            <div {...getSuggestionItemProps(suggestion, { style })}>
                              {suggestion.description}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}

                </PlacesAutocomplete>
                  </Grid>

                    { (isBloodBank ||isHospital) && (
                          <Grid container spacing={1}  > 
                          
                          {bloodGroupQuan.map((item, index) => (
                            <div>
                              <div>
                                  <span >{item.itemName}</span>
                              </div>
                              <div>
                              <TextField
                                type="number"
                                required
                                fullWidth
                                size="small"
                                style={{display: "flex", width: "95%"}}
                                inputProps={{ min: 0 }}
                                variant="outlined"
                                name="bloodGroupQuan"
                                value={item.quantity}
                                onChange={(event) => handleQuantityInput(index,event)}
                              />
                            </div>
                              {/* <div className='quantity'>
                                <input type="number" name="bloodGroupQuan" value={item.quantity} placeholder="Quantity" min="0" onChange={(event) => handleQuantityInput(index,event)}/>  
                              </div> */}
                            </div>
                          ))}
                        </Grid>
                        )}
          
            
            
            </Grid>
            <Grid>
            <progress value={progress} max="100" />
            <TextField type="file" onChange={imageHandleChange} />
            <Button onClick={imageHandleUpload}>Upload</Button>
            </Grid>

            <Box m={2} pt={2}>
            <Button 
              type="submit"
              fullWidth
              variant="contained"
              color="primary"
              className={classes.submit}
              onClick={event => {
                createUserWithEmailAndPasswordHandler(event, email, password);
              }}
            >
              Sign Up
            </Button>
            </Box>


            {/* <Button
            onClick={() => {
              try {
                signInWithGoogle();
              } catch (error) {
                console.error("Error signing in with Google", error);
              } }} >
          Sign In with Google
        </Button> */}

            <Grid container justify="flex-end">
              <Grid item>
                <Link href="/" variant="body2">
                  Already have an account? Sign in
                </Link>
              </Grid>
            </Grid>
          
          </form>
        </div>
      </Container>
  );
};

export default SignUp;