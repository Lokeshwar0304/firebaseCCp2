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
    const [ selected, setSelected ] = useState({});

    const onSelect = item => {
        setSelected(item);
      }

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
        console.log(JSON.stringify({accepted: accepted, user_id: user_id, request_id: request_id, locations:locations}))
        fetch('https://us-central1-bloodbankasaservice.cloudfunctions.net/get_request_acceptance',{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({accepted: accepted, user_id: user_id, request_id: request_id, locations:locations})
        }).then(response =>{
            return response.json();
        }).then(data =>{
            setLocations([...locations, {
                name: 'Hospital',
                    location: { 
                        lat: parseFloat(data.hospital[0]),
                        lng: parseFloat(data.hospital[1])
                    }
            },
        {
            name: 'BloodBank',
                    location: { 
                        lat: parseFloat(data.bloodBank[0]),
                        lng: parseFloat(data.bloodBank[1])
                    }
        }])
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
                                    locations.map(item => <Marker icon={item.name === 'BloodBank' ? 'http://maps.google.com/mapfiles/ms/icons/purple-dot.png' : (item.name === 'Hospital' ? 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png' : (item.name ==='Donor' ? 'http://maps.google.com/mapfiles/ms/icons/green-dot.png': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'))} title={item.name} key={item.name} position={item.location} />)
                                }
                                
                                </GoogleMap>
                        </Paper>
                    </Grid>
                </Grid>
        </div>: <></>) 
        
}
export default Notified;