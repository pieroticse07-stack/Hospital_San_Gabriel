import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { PrimerComponenteService } from './primer-componente.service';

describe('PrimerComponenteService', () => {
  let service: PrimerComponenteService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), PrimerComponenteService]
    });
    service = TestBed.inject(PrimerComponenteService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
