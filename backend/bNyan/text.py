


from .constants_ import UNICODE_REPLACEMENT_CHARACTER, NULL_CHARACTER


def default_decode( data ):
    
    default_encoding = 'windows-1252'
    
    default_text = str( data, default_encoding, errors = 'replace' )
    
    default_error_count = default_text.count( UNICODE_REPLACEMENT_CHARACTER )
    
    return ( default_text, default_encoding, default_error_count )
    



def non_failing_unicode_decode( data, encoding ):
    
    text = None
    
    try:
        
        if encoding in ( 'ISO-8859-1', 'Windows-1252', None ):
            
            # ok, the site delivered one of these non-utf-8 'default' encodings. this is probably actually requests filling this in as default
            # we don't want to trust these because they are very permissive sets and'll usually decode garbage without errors
            # we want chardet to have a proper look
            
            raise LookupError()
            
        
        text = str( data, encoding )
        
    except ( UnicodeDecodeError, LookupError ) as e:
        
        try:
            
            if isinstance( e, UnicodeDecodeError ):
                
                text = str( data, encoding, errors = 'replace' )
                
            if text is None:
                
                try:
                    
                    ( default_text, default_encoding, default_error_count ) = default_decode( data )
                    
                    text = default_text
                    encoding = default_encoding
                    
                except:
                    
                    text = 'Could not decode the page--problem with given encoding "{}".'.format( encoding )
                    encoding = 'utf-8'
            
            if text is None:
                
                raise Exception()
                
            
        except Exception as e:
            
            text = 'Unfortunately, could not decode the page with given encoding "{}".'.format( encoding )
            encoding = 'utf-8'
            
        
    
    if NULL_CHARACTER in text:
        
        # I guess this is valid in unicode for some reason
        # funnily enough, it is not replaced by 'replace'
        # nor does it raise an error in normal str creation
        
        text = text.replace( NULL_CHARACTER, '' )
        
    
    return ( text, encoding )
    
