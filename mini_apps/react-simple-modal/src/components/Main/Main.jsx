import React, { useState } from "react";
import { SimpleModal } from "../SimpleModal/SimpleModal";
import "./Main.css";

export const Main = () => {
  const [modalInfoIsOpen, setModalInfoOpen] = useState(false);
  const [modalAboutIsOpen, setModalAboutOpen] = useState(false);
  const [modalDataIsOpen, setModalDataOpen] = useState(false);

  return (
    <main className="main">
      <section className="section">
        <button
          className="modal-show-button"
          onClick={() => setModalInfoOpen(true)}
        >
          Modal Info
        </button>
        <button
          className="modal-show-button"
          onClick={() => setModalAboutOpen(true)}
        >
          Modal About
        </button>
        <button
          className="modal-show-button"
          onClick={() => setModalDataOpen(true)}
        >
          Modal Data
        </button>

        <SimpleModal
          isOpen={modalInfoIsOpen}
          onClose={() => setModalInfoOpen(false)}
        >
          <h2>Modal Info</h2>
          <p>
            Lorem ipsum dolor sit, amet consectetur adipisicing elit. Quo,
            dolorum dolore vero eligendi cum iusto ea quam perspiciatis
            veritatis rem cupiditate a in, aliquam pariatur.
          </p>
        </SimpleModal>

        <SimpleModal
          isOpen={modalAboutIsOpen}
          onClose={() => setModalAboutOpen(false)}
        >
          <h2>Modal About</h2>
          <p>
            Lorem ipsum dolor sit amet consectetur, adipisicing elit. Ducimus
            placeat commodi distinctio sunt nesciunt quia provident repudiandae
            totam laudantium vel maiores rerum cupiditate, hic repellat error
            odio itaque ratione blanditiis? Dolorum excepturi quibusdam repellat
            illum, recusandae consectetur veniam velit minima, totam assumenda
            dignissimos iure illo obcaecati consequatur maiores. Molestiae, ut.
          </p>
        </SimpleModal>

        <SimpleModal
          isOpen={modalDataIsOpen}
          onClose={() => setModalDataOpen(false)}
        >
          <h2>Modal Data</h2>
          <p>
            Lorem, ipsum dolor sit amet consectetur adipisicing elit. Maxime
            nemo quae, dolorem molestias aliquam aut quia minima eos quis
            sapiente unde veniam aliquid sequi saepe iste exercitationem,
            nesciunt enim doloremque. Veritatis, quaerat! Beatae corrupti velit
            officia aspernatur impedit nam mollitia laborum itaque totam
            explicabo obcaecati, quidem dignissimos consectetur hic soluta, in
            eaque enim possimus fuga? Numquam sint hic aut debitis nobis.
            Doloremque magni laborum ab quidem velit maxime, neque quia.
          </p>
          <p>
            Lorem, ipsum dolor sit amet consectetur adipisicing elit. Optio non,
            incidunt neque delectus asperiores nam! Tenetur reprehenderit hic
            eum quasi quia impedit veritatis laudantium facere optio odit
            pariatur, quo corrupti ratione? Consectetur numquam aliquid cumque
            ipsam repellat id ducimus, optio blanditiis maiores fuga eligendi
            quia.
          </p>
        </SimpleModal>
      </section>
    </main>
  );
};
