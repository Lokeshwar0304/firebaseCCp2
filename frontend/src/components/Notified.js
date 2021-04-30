import React, {useState, useEffect}  from 'react';
import { GoogleMap, useJsApiLoader, Marker,InfoWindow } from '@react-google-maps/api';
import { Button, Grid, Paper, Typography, CircularProgress } from '@material-ui/core';


const gridStyles =  {paper: { height:'90vh' }}


const containerStyle = {
    width: '100%',
    height: '100%'
  };
  
  const center = {
    lat: 33.4092,
    lng: -111.9203
  };

const Notified = (props) => {

    const [locations, setLocations] = useState([]);
    const [haveData, setHaveData] = useState(false);

    let user_id = props.user_id
    let request_id = props.request_id
    useEffect(() => {
        const body = {
            user_id: user_id,
            request_id: request_id
        }
        fetch('https://us-central1-bloodbankasaservice.cloudfunctions.net/get_blood_request',{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(body)
        }).then(response =>{
            return response.json();
        }).then(data =>{
            console.log(data)
            setLocations([
                {
                    name: 'Donor',
                    location: { 
                        lat: parseFloat(data.donar.coordinates.latitude),
                        lng: parseFloat(data.donar.coordinates.longitude)
                    }
                },
                {
                    name: 'Receiver',
                    location: { 
                        lat: parseFloat(data.receiver.coordinates.latitude),
                        lng: parseFloat(data.receiver.coordinates.longitude)
                    }
                }
            ])
            setHaveData(true)
        }).catch(error => {
            console.log(error)
        });
    }, [user_id, request_id])

    const acceptRequest = (event, accepted) => {
        fetch('https://us-central1-bloodbankasaservice.cloudfunctions.net/get_request_acceptance',{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({accepted: accepted, user_id: user_id, request_id: request_id})
        }).then(response =>{
            return response.json();
        }).then(data =>{

        }).catch(error => {
            console.log(error)
        });
    }
    
    const { isLoaded } = useJsApiLoader({
        id: 'google-map-script',
        googleMapsApiKey: "AIzaSyCSngnFVuMXGnhdO2ZBsN7kYk_o7L9PVys"
    })

//   return  isLoaded? 
  return (haveData ? <div>
                <Grid container justify="center" alignItems="center"style={{ minHeight: '10vh' }}>
                    <Button variant="contained" style={{marginRight:"5px"}} size="large" color="primary" onClick = {(event) => {acceptRequest(event, true)}}>
                        Accept Request
                    </Button>
                    <Button variant="contained" style={{marginLeft:"5px"}} size="large" color="secondary" onClick = {(event) => {acceptRequest(event, false)}}>
                        Reject Request
                    </Button>
                </Grid>
                <Grid container>
                    <Grid item sm >
                        <Paper style={gridStyles.paper}>
                            <GoogleMap
                                mapContainerStyle={containerStyle}
                                zoom={8}
                                center={center}>
                                {
                                    locations.map(item => <Marker key={item.name} position={item.location} />)
                                }
                                </GoogleMap>
                        </Paper>
                    </Grid>
                </Grid>
        </div>: <></>) 
        
}
export default Notified;