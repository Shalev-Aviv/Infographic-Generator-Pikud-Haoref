import './Navigation.css';

function Navigation() {
  return (
    <nav className="navbar">
      <div className="container">
        <button className='right logo-button'>
          <img className="logos" src='Pikud Haoref Logo.png' />
          <img className="logos" src='Israel Symbol.svg' />
          <span className='name'>פיקוד העורף</span>
        </button>
      </div>
    </nav>
  );
}

export default Navigation;