
import firebase from "firebase/app";
import "firebase/auth";
import "firebase/firestore";
import "firebase/functions";
import "firebase/storage";

var firebaseConfig = {
  apiKey: "AIzaSyDgZ8UZ0mySA3qTtlj3tJ1OZleyDAsuw84",
  authDomain: "bloodbankasaservice.firebaseapp.com",
  projectId: "bloodbankasaservice",
  storageBucket: "bloodbankasaservice.appspot.com",
  messagingSenderId: "621697739059",
  appId: "1:621697739059:web:8a6c3fe1d11046c74f7646"
};
const get_base_url= 'https://us-central1-bloodbankasaservice.cloudfunctions.net/get_nearest_service'
// Initialize Firebase
firebase.initializeApp(firebaseConfig);


export const auth = firebase.auth();
export const firestore = firebase.firestore();
export const storage = firebase.storage();
export const requests = firestore.collection("/Requests");

const provider = new firebase.auth.GoogleAuthProvider();
export const signInWithGoogle = () => {
  auth.signInWithPopup(provider);
};
export const generateUserDocument = async (user,additionalData) => {
  if (!user) return;
  const userRef = firestore.doc(`User/${user.uid}`);
  const snapshot = await userRef.get();
  
  if (!snapshot.exists) {
    const { email, displayName, photoURL } = user;
    try {
      await userRef.set({
        displayName,
        email,
        photoURL,
        ...additionalData
      });
      
    return getUserDocument(user.uid); 
    } catch (error) {
      console.error("Error creating user document", error);
    }
  }
  return getUserDocument(user.uid);
};
const getUserDocument = async uid => {
  if (!uid) return null;
  try {
    const userDocument = await firestore.doc(`User/${uid}`).get();
    
    return {
      uid,
      ...userDocument.data()
    };
  } catch (error) {
    console.error("Error fetching user", error);
  }
};
// export const generateUserRequest = async (request) => {
//   if (!request) return;
//   // const db= firestore.collection("/Requests");
//   // const  reqRef = await db.add(request);
//   // Add a new document with a generated id.
//   firestore.collection("/Requests").add(request)
//   .then(function(docRef) {
//    // console.log("Document written with ID: ", docRef.id);
//       axios.get(get_base_url+docRef.id).then(response =>{
//         console.log(response['data'])
//       }).catch(
//         error => {console.log("Error fetching request data: ", error); 
//       })
//   })
//   .catch(function(error) {
//     console.error("Error adding document: ", error);
//   });
// };
export const generateUserRequest = (request) => {
  if (!request) return;
  firestore.collection("/Requests").add(request)
  .then( function(docRef) {
      const body = {fetchId : docRef.id }
      fetch(get_base_url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
        ,body: JSON.stringify(body)
          }).then(response =>{
            console.log(response.json());
          }).then(data =>{
            // console.log(data)
            console.log(data)
          }).catch(error => {
            console.log(error)
          });
        })
  .catch(function(error) {
    console.error("Error adding document: ", error);
  });
};