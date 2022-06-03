import React from 'react'
import Nav from "../elements/Navbar";


import { getData } from '../../requests';
import objectEmpty from '../../util';
import ImageContainer from '../elements/ImageContainer';
import API_ENDPOINTS from '../../constant';

import "../../css/video.css";
import "../../css/bootstrap.min.css";
import "../../css/ImagePage.css";
import { useParams } from 'react-router-dom';

export default function ImagePage(props)
{
    const { cookies } = props;

    const [fileInfo    , setFileInfo] = React.useState(null);
    const [tagDisplay  , setTagDisplay] = React.useState(null);
    const [imgDisplay  , setImgDisplay] = React.useState(null);
    const query = new URLSearchParams(window.location.search);
    const params = useParams();
    const fileId   = params.id;

    if(isNaN(fileId) || fileId < 0)
    {
        return (
                <div className="apply-font">
                    <Nav {...nprops}></Nav>
                    <div className='container'>
                        <div className='row'>
                            <div className='col'>
                                404 Image Not Found
                            </div>
                        </div>
                    </div>
                </div>
            )
    }

    let nprops = {
        brand : "~4Nyan~",
        displayUser : cookies.get("username")
    };

    React.useEffect(() => 
    {
        get_file_info();
    }, []);

    async function get_file_info()
    {
        const get_endpoint_1 = API_ENDPOINTS.backend_ref + API_ENDPOINTS.search.get_files + "?fid=" + fileId;
        const get_endpoint_2 = API_ENDPOINTS.backend_ref + API_ENDPOINTS.search.get_file_tags + "?fid=" + fileId;

        const headers = {

        };

        let fileInfo = {

        };

        try 
        {
            const req_info = await getData(get_endpoint_1, headers);

            if(req_info.status !== 200)
            {
                throw "could not fetch file info";
            }

            fileInfo.content = JSON.parse(req_info.response).content[0];
        }
        catch(e)
        {
            console.log(e);
            fileInfo.content = null;
        }

        try 
        {
            const req_tagv = await getData(get_endpoint_2, headers);

            if(req_tagv.status !== 200)
            {
                throw "could not fetch tags";
            }
                        
            fileInfo.tags = JSON.parse(req_tagv.response)[fileId];
        }
        catch(e)
        {
            console.log(e);
            fileInfo.tags = null;
        }

        setFileInfo(fileInfo);

        let tagDisp = [];
        for(let i of fileInfo.tags)
        {
            tagDisp.push(
                <div key={i.tag_id}>
                    {i.namespace + ":" + i.tag}
                </div>
            );
        }

        setTagDisplay(tagDisp);

        console.log(fileInfo);
        let url = "";
        
        if(fileInfo.content)
            if(fileInfo.content.static_url.content.length >0)
                url = fileInfo.content.static_url.content[0];

        setImgDisplay(
                <img className='fit' src={url}></img>
        );
    }

    return (
        <div className="apply-font">
            
            <Nav {...nprops}></Nav>

            <div className='container'>

                <div className='row'>

                <div className='col'>
                    {tagDisplay}
                </div>

                <div className='col'>
                    {imgDisplay}
                </div>
                </div>
            </div>
        </div>
    )
}
