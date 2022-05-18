import React from 'react'
import Nav from "../elements/Navbar";

import postData from '../../requests';
import API_ENDPOINTS from '../../constant';
import "../../css/bootstrap.min.css";

export default function CreateTag(props)
{
    const { cookies } = props;

    const textb = React.useRef("");

    let nprops = {
        brand : "~4Nyan~",
        displayUser : cookies.get("username")
    };

    async function buttonClick(e)
    {
        e.preventDefault();

        // const token      = cookies.get("access_token");
        // const token_type = cookies.get("token_type");

        // if (!token || !token_type)
        //     return; 

        const upload_endpoint = API_ENDPOINTS.backend_ref + API_ENDPOINTS.create_tag;

        const data = {
            "tasg": textb.current.value
          };

        console.log(textb.current.value);

        const headers = {
            "content-type" : 'application/json',
        };

        try 
        {
            const req = await postData(upload_endpoint, JSON.stringify(data), headers);

            console.log(req);
        }
        catch (e)
        {
            console.log("error ono");
            console.log(e);
        }

    }
    
    return (
        <div className="apply-font">
            
            <Nav {...nprops}></Nav>

            <div className='container'>

                <form>
                    <input type="text" ref={textb}></input>
                    <button onClick={buttonClick}>Create</button>
                </form>

                
            </div>
        </div>
    )
}
