"use strict;"

//funzione di ricerca episodio
function cercaEpisodio()
{
    let input=document.getElementById("barraDiRicerca").value
    input=input.toLowerCase();
    let episodi=document.getElementsByClassName("titoloEpDaCercare");
    
    for(i=0; i<episodi.length; i++)
    {
        let episodio=episodi[i];
        let titoloEpisodio=episodio.innerHTML.toLowerCase();
        let descrizione=episodio.nextElementSibling
        let testoDescrizione=descrizione.innerHTML.toLowerCase();
        
        if( !titoloEpisodio.includes(input) && !testoDescrizione.includes(input) || input.length==0 )
            episodio.classList.add("nascondi");
        else
            episodio.classList.remove("nascondi");
    }
}

//funzione che nascone il footer nella pagina del profilo se è visualizzato il carousel (se ci sono 2 o più serie)
window.onload = function nascondiFooter()
{
    let nascondi=document.getElementById("nascondiFooter").innerHTML
    footer=document.getElementById("myFooter")

    if(nascondi==1)
        footer.classList.add("nascondi");
}

