import React from 'react'
import Navbar from "../elements/Navbar";
import FileUpload from '../elements/FileUpload';

import postData from '../../requests';

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

    async function beginUpload(e)
    {
        // prevents the form from submitting 
        e.preventDefault();

        if(!files || files.length < 1)
            return;

        const token      = cookies.get("access_token");
        const token_type = cookies.get("token_type");

        if (!token || !token_type)
            return; 

        let message = []
        for(let f of files)
        {
            const upload_endpoint = API_ENDPOINTS.backend_ref + API_ENDPOINTS.upload_file;
            const totalSize       = f.size;
            const data            = new FormData();

            const headers = {
                Authorization :  `${token_type} ${token}`,
            };

            function progress(event)
            {
                setProgress(`${f.name}: uploaded ${event.loaded} / ${totalSize} bytes`);
            }

            data.append("data", f, f.name);
            
            await postData(upload_endpoint, data, headers, progress)
                .then(e    => message.push(<div style={{color:"green"}} key={f.name}>{f.name}: {e.status}</div>))
                .catch(err => message.push(<div style={{color:"red"}}   key={f.name}>{f.name}: {err.status}</div>));
        }
        
        setMessage(message);
    }

    function generatePreview(e)
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
            r.push(<FileUpload {...props} key={i}></FileUpload>);
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
                                    required=""
                                    multiple
                                    ref={fileUpload}
                                    onChange={generatePreview}></input>
                            </div>

                            <div className='row'>
                                <button id="pink-button" onClick={beginUpload}><strong>Upload</strong></button>
                            </div>

                            <div className='row'>
                                <span>
                                    {uploadProgress}
                                </span>
                            </div>

                            <div className='row'>
                                <span>
                                    {messageBox}
                                </span>
                            </div>
                    </form>

                    <div className='col preview-container'>
                        {renderPreview()}
                    </div>
                </div>
            </div>
        </div>
    )
}
