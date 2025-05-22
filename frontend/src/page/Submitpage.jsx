import { useRef } from 'react';
import submitImage from '../assets/submit.png';

function Submit() {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const files = e.target.files;
    if (files.length) {
      console.log("Files selected:", files);
      // You can process files or folders here
    }
  };

  return (
    <div className="submit-image-container">
      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        style={{ display: 'none' }}
        webkitdirectory=""
        directory=""
      />

      {/* Clickable image */}
      <div className="submit-image" onClick={() => fileInputRef.current.click()}>
        <img src={submitImage} alt="Submit" />
      </div>
    </div>
  );
}

export default Submit;
