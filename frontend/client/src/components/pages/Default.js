import React from 'react'
import Nav from "../elements/Navbar";


import { getData } from '../../requests';
import objectEmpty from '../../util';
import FileUpload from '../elements/FileUpload';
import API_ENDPOINTS from '../../constant';

import "../../css/video.css";
import "../../css/bootstrap.min.css";

export default function Default(props)
{
    const { cookies } = props;

    const [filePreviews, setPreview] = React.useState(null);
    const params = new URLSearchParams(window.location.search);
    const page = parseInt(params.get('page')) || 1;

    let vprops = {
        m3u8 : "http://192.168.1.149:721/static/m3u8/RnM_S4E1.m3u8",
        autoPlay : false
    };

    let nprops = {
        brand : "~4Nyan~",
        displayUser : cookies.get("username")
    };


    React.useEffect(() => 
    {
        get_files()
    }, []);


    async function get_files()
    {
        const get_endpoint = API_ENDPOINTS.backend_ref + API_ENDPOINTS.search.get_files;
        const content_tag = localStorage.getItem("content_tag") || "";

        const headers = {
            content_tag : content_tag
        }

        await getData(get_endpoint, headers)
                .then(e    => 
                    {
                        if(e.status !== 200)
                            return;
                        
                        let content = JSON.parse(e.response);
                        
                        if(objectEmpty(content))
                        {
                            content = JSON.parse(window.localStorage.getItem("content"));
                            console.log("cache hit");
                        }
                        else 
                        {
                            //Store into localStorage
                            window.localStorage.setItem("content", e.response);
                            window.localStorage.setItem("content_tag", content.content_tag);
                            console.log("cache miss");
                        }

                        console.log(content.content)

                        let display = [];
                        const max = Math.min(content.content.length, page * 25);

                        for(let i = Math.max(max - 25, 0); i < max; i++)
                        {
                            const value = content.content[i];
                            const fullUrl = value.static_url[0];
                            const thumbUrl = value.static_url[1];

                            const props = {
                                image : thumbUrl,
                                caption : value.width + " x " + value.height,
                                fileType : null ,
                                style : {
                                    width : "10%",
                                    border : "1px solid white",
                                }
                            }

                            display.push(
                            <a key={i} href={fullUrl} target="_blank" rel="noopener noreferrer">
                                <FileUpload {...props} ></FileUpload>
                            </a>);
                        }

                        setPreview(display);
                    })

                .catch(err => console.log(err.status));
    }
    
    return (
        <div className="apply-font">
            
            <Nav {...nprops}></Nav>

            <div className='container'>
                <div className='row'>
                    <div className='col' style={{"textAlign": "right"}}>
                        <a href={"/home/?page=" +(page - 1).toString()}>prev page</a>
                    </div>
                    
                    <div className='col'>
                        <a href={"/home/?page=" +(page + 1).toString()}>next page</a>    
                    </div>
                </div>

                <div className='row'>
                    <div className='col'>
                        {filePreviews}
                    </div>
                </div>
            </div>
        </div>
    )
}
