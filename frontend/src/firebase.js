import firebase from "firebase/app";
import "firebase/auth";
import "firebase/firestore";
import { functions } from "firebase";
import "firebase/storage"

var firebaseConfig = {
  apiKey: "AIzaSyDgZ8UZ0mySA3qTtlj3tJ1OZleyDAsuw84",
  authDomain: "bloodbankasaservice.firebaseapp.com",
  projectId: "bloodbankasaservice",
  storageBucket: "bloodbankasaservice.appspot.com",
  messagingSenderId: "621697739059",
  appId: "1:621697739059:web:8a6c3fe1d11046c74f7646"
};


// Initialize Firebase
firebase.initializeApp(firebaseConfig);

export const auth = firebase.auth();
export const firestore = firebase.firestore();

export const storage = firebase.storage();

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

export const generateUserRequest = async (request) => {
  console.log("infb")
  console.log(request)
  if (!request) return;
  const db= firestore.collection("/Requests");
  const  reqRef = await db.add(request);
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