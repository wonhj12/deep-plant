import "firebase/firestore";
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth"; // 코드 추가
import { getFirestore } from "firebase/firestore";
import { getStorage, } from "firebase/storage";

// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

const firebaseConfig = {
  apiKey: "AIzaSyC5jW9_1rq1VlBapU4kZqLf1OG40autdRo",
  authDomain: "deepplant-e0416.firebaseapp.com",
  projectId: "deepplant-e0416",
  storageBucket: "deepplant-e0416.appspot.com",
  messagingSenderId: "214163390785",
  appId: "1:214163390785:web:635f7ebc63fa7b4c66e1c0",
  measurementId: "G-RFHBPXMFMV"
};

const firebase=initializeApp(firebaseConfig);
const app = initializeApp(firebaseConfig);
export const db=getFirestore(app);
export const fireStore=getFirestore(firebase);;
export const auth = getAuth(app); // 코드 추가
// 고기 이미지 데이터 storage
export const storage = getStorage(app);