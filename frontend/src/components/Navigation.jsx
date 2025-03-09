import './Navigation.css';

function Navigation() {
  return (
    <nav className="navbar">
      <div className="container">
        <button className='right logo-button'>
          <img className="logos" src='/media/Pikud Haoref Logo.png' />
          <img className="logos" src='/media/Israel Symbol.svg' />
          <span className='name'>פיקוד העורף</span>
        </button>
        <div><span className='tab'>צרו קשר</span></div>
        <div><span className='tab'>צרו קשר</span></div>
        <div><span className='tab'>צרו קשר</span></div>
        <div><span className='tab'>צרו קשר</span></div>
        <div><span className='tab'>צרו קשר</span></div>
      </div>
    </nav>
  );
}

export default Navigation;