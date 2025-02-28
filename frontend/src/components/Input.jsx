import './Input.css';

function Input() {
  return (
    <div className="container">
        <textarea className="input" placeholder="הקלד כאן..."></textarea>
        <button className="submit">שלח</button>
    </div>
  );
}

export default Input;