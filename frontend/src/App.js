import './App.css';
import Navigation from './components/Navigation.jsx';
import Header from './components/Header.jsx';
import Input from './components/Input.jsx';
import Footer from './components/Footer.jsx';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <Navigation /> {/* The top section */}
        <Header /> {/* The main & secondary texts */}
        <Input /> {/* The section where the user creating the infographic */}
        <Footer /> {/* The bottom part with all the links */}
      </header>
    </div>
  );
}

export default App;
