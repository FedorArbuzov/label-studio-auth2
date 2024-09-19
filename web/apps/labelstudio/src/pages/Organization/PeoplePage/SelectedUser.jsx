import React, { useState, useEffect } from 'react';

import { format } from "date-fns";
import { NavLink } from "react-router-dom";
import { LsCross } from "../../../assets/icons";
import { Button, Userpic } from "../../../components";
import { Block, Elem } from "../../../utils/bem";
import "./SelectedUser.styl";

const UserProjectsLinks = ({ projects }) => {
  return (
    <Elem name="links-list">
      {projects.map((project) => (
        <Elem
          tag={NavLink}
          name="project-link"
          key={`project-${project.id}`}
          to={`/projects/${project.id}`}
          data-external
        >
          {project.title}
        </Elem>
      ))}
    </Elem>
  );
};

const UserProjectsAccessEditor = ({ projects, user }) => {
  const [projectStates, setProjectStates] = useState(projects);

  const handleButtonClick = (projectId, action) => {
    // Make a request to the server when the button is clicked
    fetch(`/api/projects/membership/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        'project_id': projectId,
        'user_id': user,
        'action': action
      }),
    })
      .then(response => response.json())
      .then(data => {
        console.log('Action successful:', data);
        // Update the state to reflect the change
        setProjectStates(prevState =>
          prevState.map(project =>
            project.id === projectId
              ? { ...project, has_access: action === 'add' }
              : project
          )
        );
      })
      .catch(error => {
        console.error('Error performing action:', error);
      });
  };

  return (
    <div>
      <h2>Projects</h2>
      <ul>
        {projectStates.map(project => (
          <li key={project.id}>
            {project.title}
            {project.has_access ? (
              <button 
                onClick={() => handleButtonClick(project.id, 'remove')}
                style={{ marginLeft: '10px' }}
              >
                Удалить доступ
              </button>
            ) : (
              <button 
                onClick={() => handleButtonClick(project.id, 'add')}
                style={{ marginLeft: '10px' }}
              >
                Добавить доступ
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};

export const SelectedUser = ({ user, onClose }) => {
  const [userRole, setUserRole] = useState(user.role);
  const fullName = [user.first_name, user.last_name]
    .filter((n) => !!n)
    .join(" ")
    .trim();

  useEffect(() => {
    setUserRole(user.role);
  }, [user]);

  return (
    <Block name="user-info">
      <Elem name="close" tag={Button} type="link" onClick={onClose}>
        <LsCross />
      </Elem>

      <Elem name="header">
        <Userpic user={user} style={{ width: 64, height: 64, fontSize: 28 }} />

        {fullName && <Elem name="full-name">{fullName}</Elem>}

        <Elem tag="p" name="email">
          {user.email}
        </Elem>
      </Elem>

      {user.phone && (
        <Elem name="section">
          <a href={`tel:${user.phone}`}>{user.phone}</a>
        </Elem>
      )}

      {!!user.created_projects.length && (
        <Elem name="section">
          <Elem name="section-title">Created Projects</Elem>

          <UserProjectsLinks projects={user.created_projects} />
        </Elem>
      )}

      <Elem name="section">
        <Elem name="section-title">Role</Elem>

          <Elem name="section-title">{userRole}</Elem>
            <select
              value={userRole}
              onChange={(e) => setUserRole(e.target.value)}
            >
              <option value="OWNER">OWNER</option>
              <option value="ADMINISTRATOR">ADMINISTRATOR</option>
              <option value="MANAGER">MANAGER</option>
              <option value="REVIEWER">REVIEWER</option>
              <option value="ANNOTATOR">ANNOTATOR</option>
            </select>

            <button
              onClick={() => {
                fetch(`/api/users/${user.id}/role`, {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                  },
                  body: JSON.stringify({ role: userRole }),
                })
                  .then(response => response.json())
                  .then(data => {
                    console.log('Role updated successfully:', data);
                    // Optionally update the user role in the state if needed
                  })
                  .catch(error => {
                    console.error('Error updating role:', error);
                  });
              }}
            >
              Save Role
            </button>
        </Elem>

      {!!user.annotation_count && (
        <Elem name="section">
          <Elem name="section-title">Annotations</Elem>

          <Elem name="annotation-count">{user.annotation_count}</Elem>
        </Elem>
      )}      

      {!!user.annotation_updated_count && (
        <Elem name="section">
          <Elem name="section-title">Annotations updated</Elem>

          <Elem name="annotation-count">{user.annotation_updated_count}</Elem>
        </Elem>
      )}      


      {!!user.contributed_to_projects.length && (
        <Elem name="section">
          <Elem name="section-title">Contributed to</Elem>

          <UserProjectsLinks projects={user.contributed_to_projects} />
        </Elem>
      )}

      {!!user.have_access_to_projects.length && (
        <Elem name="section">
          <Elem name="section-title">Have access to</Elem>

          <UserProjectsAccessEditor projects={user.have_access_to_projects} user={user.id} />
        </Elem>
      )}

      <Elem tag="p" name="last-active">
        Last activity on: {format(new Date(user.last_activity), "dd MMM yyyy, KK:mm a")}
      </Elem>
    </Block>
  );
};
