import React, {useState, useEffect} from "react";
import { } from '@material-ui/core';
import { } from '@material-ui/core/styles';
import { useParams } from "react-router-dom";
import { useJsApiLoader, GoogleMap, Marker } from '@react-google-maps/api';


const containerStyle = {
    width: '100%',
    height: '100%'
  };
  
  const center = {
    lat: 33.4092,
    lng: -111.9203
  };


const Notified = () => {

    let {user_id,  request_id} = useParams();
    const [locations, setLocations] = useState([]);

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
            setLocations([
                {
                    name: 'Donor',
                    location: { 
                        lat: parseFloat(data.donar.latitude),
                        lng: parseFloat(data.donar.longitude)
                    }
                },
                {
                    name: 'Receiver',
                    location: { 
                        lat: parseFloat(data.receiver.latitude),
                        lng: parseFloat(data.receiver.longitude)
                    }
                }
            ])
        }).catch(error => {
            console.log(error)
        });
    }, [user_id, request_id])

    const { isLoaded } = useJsApiLoader({
        id: 'google-map-script',
        googleMapsApiKey: "AIzaSyCSngnFVuMXGnhdO2ZBsN7kYk_o7L9PVys"
    })


    return isLoaded? (<GoogleMap
            mapContainerStyle={containerStyle}
            zoom={13}
            center={center}>
            {
                locations.map( item => {
                    return (
                        <Marker key={item.name} position={item.location} />
                    )
                }
                )
            }
        </GoogleMap>):<></>;
}

export default Notified;
