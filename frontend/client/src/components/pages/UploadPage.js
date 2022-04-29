import React from 'react'
import Navbar from "../elements/Navbar";
import FileUpload from '../elements/FileUpload';

import "../../css/LoginRegister.css"
import "../../css/UploadPage.css"
import "../../css/bootstrap.min.css"
import "../../css/global.css"

import API_ENDPOINTS from '../../constant';

export default function UploadPage(props)
{
    const { cookies } = props;

    const [files       , setFiles  ] = React.useState([]);
    const [filePreviews, setPreview] = React.useState([]);
    const [messageBox  , setMessage] = React.useState([]);
    const [uploadProgress, setProgress] = React.useState("");

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

        let message = []
        for(let f of files)
        {
            const totalSize = f.size;
            const data = new FormData();

            // Update the formData object
            data.append("data", f, f.name);
            
            let request = new XMLHttpRequest();
            
            // upload progress for current file
            request.upload.onprogress = (event) => 
            {
                setProgress(`'${f.name}: uploaded ${event.loaded} / ${totalSize} bytes`)
            }
            
            // on request goes through, handle the response
            request.onload = function () 
            {
                if(request.status == 200)
                {
                    message.push(<div style={{color:"green"}}>'{f.name}': upload status: {request.status.toString()}</div>);
                }
                else 
                {
                    message.push(<div style={{color:"red"}}>'{f.name}': upload status: {request.status.toString()}</div>);
                }
            };

            request.open('POST', API_ENDPOINTS.backend_ref + API_ENDPOINTS.upload_file, true);

            // send the data
            request.send(data);
            setMessage(message);
        }

        setMessage(message);
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
        // let i = 0;
        for (let f of _files) 
        {
            newFiles.push(f);
            newPreview.push(URL.createObjectURL(f));
        }

        setFiles(newFiles);
        setPreview(newPreview);
    }

  
    function renderPreview()
    {
        let r = []
        for(let i = 0; i < files.length; i++)
        {
            let props = {
                image : filePreviews[i],
                caption : files[i].name,
                fileType : files[i].type
                // onClick : (e) => removePreviewClick(e, i),
            }
            r.push(<FileUpload {...props}></FileUpload>);
        }
        return r;
    }
    
    return (
        <div className="apply-font">
            <Navbar {...nprops}></Navbar>

            <div className='container'>
                    <div className='row'>

                    <form className='col-lg-4 col-md-8 col-sm-fill'>
                            <div className='row' >
                                <input type="file"     
                                    id="signup-username" 
                                    placeholder="username"
                                    // required=""
                                    multiple
                                    ref={fileUpload}
                                    onChange={uploadFile}></input>
                            </div>

                            <div className='row'>
                                <button id="pink-button" onClick={beginUpload}><strong>Upload</strong></button>
                            </div>

                            <row>
                                {uploadProgress}
                            </row>
                            <row>
                                {messageBox}
                            </row>
                    </form>

                    <div className='col preview-container'>
                        {renderPreview()}
                    </div>
                </div>
            </div>
        </div>
    )
}
