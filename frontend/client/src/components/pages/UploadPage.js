import React from 'react'
import Navbar from "../elements/Navbar";


import "../../css/LoginRegister.css"

import "../../css/bootstrap.min.css"
import "../../css/global.css"

import API_ENDPOINTS from '../../constant';

export default function UploadPage(props)
{
    const { cookies } = props;

    const [files       , setFiles  ] = React.useState([]);
    const [filePreviews, setPreview] = React.useState([]);

    const fileUpload = React.useRef("");


    let nprops = {
        brand : "~4Nyan~",
        displayUser : cookies.get("username")
    };

    React.useEffect(() => 
    {
        // free memory when ever this component is unmounted
        return () => 
        {
            for(let f of filePreviews)
            {
                URL.revokeObjectURL(f);
            }
        }
    });

    function beginUpload(e)
    {
        // prevents the form from submitting 
        e.preventDefault();

        if(!files || files.length < 1)
            return;

        const toUpload = files[0];
        
        const data = new FormData();

        // Update the formData object
        data.append("data", toUpload, toUpload.name);
        
        let request = new XMLHttpRequest();
        request.open('POST', API_ENDPOINTS.backend_ref + API_ENDPOINTS.upload_file, true);
        
        // send the data
        request.send(data);

        // on request goes through, handle the resposne
        request.onload = function () 
        {
            let response = JSON.parse(request.response);

            console.log(response);

            if(request.status != 200)
                return;

            if (!response.user_id)
                return;

            console.log("user created");
        };
    }

    function uploadFile(e)
    {
        if(!fileUpload.current.files || fileUpload.current.files.length == 0)
            return;

        const  _files =  Array.from(fileUpload.current.files);

        // // free memory from old files
        for(let f of filePreviews)
        {
            URL.revokeObjectURL(f);
        }

        // generage file list for new files 
        let newFiles = [];
        let newPreview = [];
        let i = 0;
        for (let f of _files) 
        {
            i++;

            newFiles.push(f);

            // only preview 5 images 
            if(i <= 5)
                newPreview.push(URL.createObjectURL(f));
        }

        setFiles(newFiles);
        setPreview(newPreview);
    }

    
    return (
      <div className="apply-font">
          <Navbar {...nprops}></Navbar>

          <div className="content">
                
                <form className='col'>
                    <div className='row'>

                        <input type="file"     
                                id="signup-username" 
                                placeholder="username"
                                required=""
                                multiple
                                ref={fileUpload}
                                onChange={uploadFile}></input>
                    </div>

                    <div className='row'>
                        <button id="pink-button" onClick={beginUpload}><strong>Upload</strong></button>
                    </div>
                    
                    </form>

                <div className='col' style={{"float":"right", "overflow-y": "scroll", "margin-left" : "50px", "height" : "90vh"}}>

                        {files &&
                        filePreviews.map(e => 
                        {
                            return <img src={e} style={{"display" : "block"}}></img>
                        })
                        } 
                </div>
      </div>
  </div>
    )
}
