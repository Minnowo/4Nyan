import React from 'react'
import Nav from "../elements/Navbar";


import { getData } from '../../requests';
import objectEmpty from '../../util';
import ImageContainer from '../elements/ImageContainer';
import API_ENDPOINTS from '../../constant';

import "../../css/video.css";
import "../../css/bootstrap.min.css";

export default function ImagesPage(props)
{
    const { cookies } = props;

    const [filePreviews, setPreview] = React.useState(null);
    const params = new URLSearchParams(window.location.search);
    const page   = parseInt(params.get('page')) || 1;

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

        try 
        {
            const req = await getData(get_endpoint, headers);

            if(req.status !== 200)
                return;
                        
            let content = JSON.parse(req.response);
            
            if(objectEmpty(content))
            {
                content = JSON.parse(window.localStorage.getItem("content"));
                console.log("cache hit");
            }
            else 
            {
                //Store into localStorage
                window.localStorage.setItem("content", req.response);
                window.localStorage.setItem("content_tag", content.content_tag);
                console.log("cache miss");
            }

            let display = [];
            const max = Math.min(content.content.length, page * 25);

            for(let i = Math.max(max - 25, 0); i < max; i++)
            {
                const value       = content.content[i];
                const static_urls = value.static_url;

                const props = {
                    image : static_urls.thumbs[0],
                    caption : value.width + " x " + value.height,
                    fileType : null ,
                    style : {
                        width : "200px",
                        border : "1px solid white",
                        "verticalAlign" : "middle",

                        // "display": "flex",
                        // width: "195px",
                        // height: "185px",
                        // "margin-top": "20px",
                        // "align-items": "center",
                        // "justify-content": "center"
                    }
                }

                display.push(
                <a key={i} href={static_urls.content[0]} target="_blank" rel="noopener noreferrer">
                    <ImageContainer {...props} ></ImageContainer>
                </a>);
            }

            setPreview(display);
        }
        catch(e)
        {

        }
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
