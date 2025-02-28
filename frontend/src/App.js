import './App.css';
import Navigation from './components/Navigation.jsx';
import Header from './components/Header.jsx';
import Input from './components/Input.jsx';
import Footer from './components/Footer.jsx';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <Navigation />
        <Header />
        <Input />
        <Footer />
      </header>
    </div>
  );
}

export default App;
