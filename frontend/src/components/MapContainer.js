import React, {useState}  from 'react';
import { GoogleMap, useJsApiLoader, Marker,InfoWindow } from '@react-google-maps/api';

const locations = [
    {
      name: "Location 1",
      location: { 
        lat: 33.409663,
        lng: -111.897216
      },
    },
    {
      name: "Location 2",
      location: { 
        lat: 34.409663,
        lng: -112.897216
      },
    },
    {
      name: "Location 3",
      location: { 
        lat: 33.439663,
        lng: -111.998
      },
    }
  ];


const containerStyle = {
    width: '100%',
    height: '100%'
  };
  
  const center = {
    lat: 33.4092,
    lng: -111.9203
  };

const MapContainer = () => {

  const [ selected, setSelected ] = useState({});
  
  const onSelect = item => {
    setSelected(item);
  }
  
    const { isLoaded } = useJsApiLoader({
        id: 'google-map-script',
        googleMapsApiKey: "AIzaSyCSngnFVuMXGnhdO2ZBsN7kYk_o7L9PVys"
      })

  return  isLoaded? (
        <GoogleMap
          mapContainerStyle={containerStyle}
          zoom={13}
          center={center}>
        {
            locations.map(item => {
              return (
              <Marker key={item.name} position={item.location} onClick={() => onSelect(item)} />
              )
            })
         }
         {
            selected.location && 
            (
              <InfoWindow
              position={selected.location}
              clickable={true}
              onCloseClick={() => setSelected({})}>
              <p>{selected.name}</p>
            </InfoWindow>
            )
         }
        </GoogleMap> ) : <></>
}
export default MapContainer;