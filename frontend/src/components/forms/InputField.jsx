// src/components/forms/InputField.jsx
import React from 'react';

const InputField = ({ label, type, id, value, onChange }) => (
  <div className="form__group">
    <label htmlFor={id} className="form__label">{label}:</label>
    <input
      type={type}
      id={id}
      value={value}
      onChange={onChange}
      required
      className="form__input"
    />
  </div>
);

export default InputField;
