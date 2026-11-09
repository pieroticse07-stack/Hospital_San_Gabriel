import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { form, FormField } from '@angular/forms/signals';
import { PrimerComponenteService } from '../../services/primer-componente.service';
import { Persona } from '../../interfaces/persona';

@Component({
  selector: 'app-formulario-persona',
  standalone: true,
  imports: [CommonModule, FormField],
  templateUrl: './formulario-persona.html',
  styleUrl: './formulario-persona.css'
})
export class FormularioPersonaComponent implements OnInit {
  private readonly personaService = inject(PrimerComponenteService);

  // Signals para el estado
  readonly personas = signal<Persona[]>([]);
  readonly cargando = signal<boolean>(false);
  readonly guardando = signal<boolean>(false);
  readonly mensaje = signal<{ tipo: 'success' | 'danger'; texto: string } | null>(null);
  readonly editandoId = signal<number | null>(null);

  // Signal con el modelo de la persona
  readonly personaModel = signal<Persona>({
    Nombre: '',
    Email: '',
    Telefono: '',
    Ciudad: '',
    Edad: 0
  });

  // Signal Form oficial con la directiva [formField]
  readonly personaForm = form(this.personaModel);

  ngOnInit(): void {
    this.cargarPersonas();
  }

  cargarPersonas(): void {
    this.cargando.set(true);
    this.personaService.listar().subscribe({
      next: (data) => {
        this.personas.set(data);
        this.cargando.set(false);
      },
      error: (err) => {
        this.cargando.set(false);
        this.procesarError(err, 'Error al cargar los registros');
      }
    });
  }

  guardar(): void {
    const formValues = this.personaForm().value();
    const raw = formValues || this.personaModel();

    if (!raw.Nombre || !raw.Nombre.trim()) {
      this.mostrarMensaje('danger', 'El nombre es obligatorio.');
      return;
    }
    if (!raw.Email || !raw.Email.trim()) {
      this.mostrarMensaje('danger', 'El correo electrónico es obligatorio.');
      return;
    }

    const payload: Persona = {
      Nombre: raw.Nombre.trim(),
      Email: raw.Email.trim(),
      Telefono: (raw.Telefono || '').trim(),
      Ciudad: (raw.Ciudad || '').trim(),
      Edad: Number(raw.Edad) || 0
    };

    const id = this.editandoId();
    this.guardando.set(true);

    if (id !== null) {
      this.personaService.actualizar(id, payload).subscribe({
        next: () => {
          this.guardando.set(false);
          this.mostrarMensaje('success', 'Registro actualizado correctamente.');
          this.cancelarEdicion();
          this.cargarPersonas();
        },
        error: (err) => {
          this.guardando.set(false);
          this.procesarError(err, 'Error al actualizar el registro');
        }
      });
    } else {
      this.personaService.crear(payload).subscribe({
        next: () => {
          this.guardando.set(false);
          this.mostrarMensaje('success', 'Persona registrada exitosamente.');
          this.cancelarEdicion();
          this.cargarPersonas();
        },
        error: (err) => {
          this.guardando.set(false);
          this.procesarError(err, 'Error al registrar la persona');
        }
      });
    }
  }

  editar(persona: Persona): void {
    if (persona.PacienteID !== undefined) {
      this.editandoId.set(persona.PacienteID);
    }
    this.personaModel.set({
      Nombre: persona.Nombre,
      Email: persona.Email,
      Telefono: persona.Telefono,
      Ciudad: persona.Ciudad,
      Edad: persona.Edad
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  eliminar(id?: number): void {
    if (id === undefined) return;
    if (confirm(`¿Está seguro de eliminar el registro #${id}?`)) {
      this.personaService.eliminar(id).subscribe({
        next: () => {
          this.mostrarMensaje('success', 'Registro eliminado correctamente.');
          this.cargarPersonas();
        },
        error: (err) => {
          this.procesarError(err, 'No se pudo eliminar el registro');
        }
      });
    }
  }

  cancelarEdicion(): void {
    this.editandoId.set(null);
    this.personaModel.set({
      Nombre: '',
      Email: '',
      Telefono: '',
      Ciudad: '',
      Edad: 0
    });
  }

  private procesarError(err: any, fallback: string): void {
    if (err.status === 0) {
      this.mostrarMensaje(
        'danger',
        'No se puede conectar con el backend en http://localhost:8000. Verifica que esté corriendo en la terminal.'
      );
    } else if (err.error?.detail) {
      const detalle = typeof err.error.detail === 'string' ? err.error.detail : JSON.stringify(err.error.detail);
      this.mostrarMensaje('danger', `${fallback}: ${detalle}`);
    } else {
      this.mostrarMensaje('danger', `${fallback}. (Código HTTP ${err.status})`);
    }
  }

  private mostrarMensaje(tipo: 'success' | 'danger', texto: string): void {
    this.mensaje.set({ tipo, texto });
  }
}
