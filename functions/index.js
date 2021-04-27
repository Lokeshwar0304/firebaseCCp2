
const functions = require("firebase-functions");
const admin = require("firebase-admin");
admin.initializeApp();
// const firestore = admin.firestore();
// Initialize Firebase
exports.printTimeStamp = functions.firestore
    .document("Requests/{docId}")
    .onCreate((snap, context) => {
      const request = snap.data();
      functions.logger.info(request.email, {structuredData: true});
      const user= admin.firestore.collection("User")
          .where("email", "==", request.email);
      user.get().then((querySnapshot) => {
        querySnapshot.forEach((documentSnapshot) => {
          functions.logger.info(documentSnapshot.data(),
              {structuredData: true});
        });
      });
    });


