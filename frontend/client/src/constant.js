
const API_ENDPOINTS = {
    backend_ref : "http://192.168.1.149:721/",
    login : "auth/token/",
    register : "create/user/",
    upload_file : "create/file/",
    static : {
        video : "static/v/",
        image : "static/i/",
        m38u  : "static/m3u8/",
    }
};

export const MAX_PASSWORD_LENGTH = 96;
export const MIN_PASSWORD_LENGTH = 1;

export const MAX_USERNAME_LENGTH = 32;
export const MIN_USERNAME_LENGTH = 4;

export default API_ENDPOINTS;