import React from 'react'
import Nav from "../elements/Navbar";


import { getData } from '../../requests';
import objectEmpty from '../../util';
import ImageContainer from '../elements/ImageContainer';
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
