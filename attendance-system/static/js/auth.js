// Firebase Configuration (Ensure Firebase is Initialized in Python)
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-auth.js";
import { getFirestore, doc, setDoc } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-firestore.js";
import { getStorage, ref, uploadBytes, getDownloadURL } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-storage.js";

// Firebase Config (Ensure This Matches Your Firebase Project)
const firebaseConfig = {
  apiKey: "AIzaSyAhvUQC6SWtZ8aFMpRu0owWT1MVcq_t_Fo",
  authDomain: "attendence-list-lbs.firebaseapp.com",
  databaseURL: "https://attendence-list-lbs-default-rtdb.firebaseio.com",
  projectId: "attendence-list-lbs",
  storageBucket: "attendence-list-lbs.firebasestorage.app",
  messagingSenderId: "874744289039",
  appId: "1:874744289039:web:67d16e57a1c4ca0a48107a"
};

// Initialize Firebase Services
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const storage = getStorage(app);

// Handle Signup Form Submission
document.getElementById('signupForm').addEventListener('submit', async function (event) {
    event.preventDefault(); // Prevent Page Reload

    // Get Form Values
    const name = event.target.name.value;
    const branch = event.target.branch.value;
    const number = event.target.number.value;
    const email = event.target.eemail.value;
    const password = event.target.ppwd.value;
    const photo = event.target.photo.files[0];

    try {
        // Create User in Firebase Authentication
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;

        // Upload Photo to Firebase Storage
        const storageRef = ref(storage, `profile_pics/${user.uid}`);
        await uploadBytes(storageRef, photo);
        const photoURL = await getDownloadURL(storageRef);

        // Save User Data in Firestore
        await setDoc(doc(db, "students", user.uid), {
            name, branch, number, email, photoURL
        });

        Swal.fire("Success!", "Signup Successful!", "success");

    } catch (error) {
        Swal.fire("Error!", error.message, "error");
    }
});
