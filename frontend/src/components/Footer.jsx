import './Footer.css';

function Footer() {
  return (
    <div className="footer">
        <div className='side'>
            <h4>עקבו אחרינו גם ברשתות</h4>
            <ul>
                <li className='social-media'>
                    <a className='logo' id='youtube' href="https://www.youtube.com/user/pakar2008" target='_blank' ></a>
                </li>
                <li className='social-media'>
                    <a className='logo' id='facebook' href="https://www.facebook.com/PikudHaoref/" target='_blank' ></a>
                </li>
                <li className='social-media'>
                    <a className='logo' id='instagram' href="https://www.instagram.com/pikudhaoref?igsh=eXRhMzljMnBlZ2Fo" target='_blank' ></a>
                </li>
                <li className='social-media'>
                    <a className='logo' id='x' href="https://twitter.com/PikudHaoref1" target='_blank' ></a>
                </li>
                <li className='social-media'>
                    <a className='logo' id='telegram' href="https://t.me/PikudHaOref_all" target='_blank' ></a>
                </li>
                <li className='social-media'>
                    <a className='logo' id='tiktok' href="https://www.tiktok.com/@pikud_haoref?_t=8hKGQ14FYHw&_r=1" target='_blank' ></a>
                </li>
            </ul>
        </div>
        <div className='divider'></div>
        <div className='side'>
            <h4>תוכלו למצוא אותנו גם ב-</h4>
            <ul>
                <li className='downloads' >
                    <a className='os' id='google-play' href="http://bit.ly/Oref_App_Android" target="_blank" ></a>
                </li>
                <li className='downloads' >
                    <a className='os' id='app-store' href="http://bit.ly/Oref_App_iOS" target="_blank" ></a>
                </li>
            </ul>
        </div>
    </div>
  );
}

export default Footer;