import React from 'react'
import Navbar from "../elements/Navbar";
import ImageContainer from '../elements/ImageContainer';

import postData from '../../requests';

import "../../css/LoginRegister.css"
import "../../css/UploadPage.css"
import "../../css/bootstrap.min.css"
import "../../css/global.css"

import API_ENDPOINTS from '../../constant';


// TODO: 
// add a checkbox "make this a gallery" which creates a database group and keeps the file order 
// add a drop down for category, (manga, image set, book, tv series...) 
// make an endpoint which supports these



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
    },[]);

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

        
        let uploadFile = "";
        let totalSize = 0;
        function progress(event)
        {
            setProgress(`${uploadFile}: uploaded ${event.loaded} / ${totalSize} bytes`);
        }

        let message = []
        for(let f of files)
        {
            const upload_endpoint = API_ENDPOINTS.backend_ref + API_ENDPOINTS.upload_file;
            const data            = new FormData();

            const headers = {
                Authorization :  `${token_type} ${token}`,
            };

            totalSize  = f.size;
            uploadFile = f.name;

            data.append("data", f, f.name);
            
            try 
            {
                const req = await postData(upload_endpoint, data, headers, progress);

                message.push(<div style={{color:"green"}} key={f.name}>{f.name}: {req.status}</div>);
            }
            catch(e)
            {
                message.push(<div style={{color:"red"}}   key={f.name}>{f.name}: {e.status}</div>);

                if(e.status === 401)
                {
                    break;
                }
            }
        }

        setMessage(message);        
    }

    function generatePreview(e)
    {
        if(!fileUpload.current.files || fileUpload.current.files.length === 0)
            return;

        const  _files =  Array.from(fileUpload.current.files);

        // // free memory from old files
        for(let f of filePreviews)
        {
            URL.revokeObjectURL(f);
        }

        // generage file list for new files 
        let newFiles   = [];
        let newPreview = [];
        let x = 0;

        for (let f of _files) 
        {
            newFiles.push(f);

            if (x < 5)
            {
                newPreview.push(URL.createObjectURL(f));
                ++x;
            }
        }

        setFiles(newFiles);
        setPreview(newPreview);
    }

  
    function renderPreview()
    {
        let r = []
        for(let i = 0; i < Math.min(files.length, 5); i++)
        {
            let props = {
                image    : filePreviews[i],
                caption  : files[i].name,
                fileType : files[i].type
                // onClick : (e) => removePreviewClick(e, i),
            }
            r.push(<ImageContainer {...props} key={i}></ImageContainer>);
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
